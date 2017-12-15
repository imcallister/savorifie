from django.contrib import admin, messages
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Channel, TaxCollector, UnitSale, Sale, SalesTax, Payout, PayoutLine, ProceedsAdjustment
from accountifie.gl.bmo import on_bmo_save
from accountifie.common.api import api_func
from inventory.models import Warehouse


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('label', 'counterparty',)
    list_filter = ('label', 'counterparty',)

admin.site.register(Channel, ChannelAdmin)


class TaxCollectorAdmin(admin.ModelAdmin):
    list_display = ('entity',)
    list_display_links = None
    list_editable = ('entity',)
    search_fields = ('entity',)


admin.site.register(TaxCollector, TaxCollectorAdmin)


# special signal as normal GL update doesn't work with NominalTransaction
sale_saved = django.dispatch.Signal(providing_args=[])
sale_saved.connect(on_bmo_save)


class UnitSaleInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        pass

class UnitSaleInline(admin.TabularInline):
    model = UnitSale
    can_delete = True
    extra = 0


class SalesTaxInline(admin.TabularInline):
    model = SalesTax
    can_delete = True
    extra = 0

class ProceedsAdjustmentInline(admin.TabularInline):
    model = ProceedsAdjustment
    can_delete = True
    extra = 0


class FulfillRequested(SimpleListFilter):
    title = 'requested'
    parameter_name = 'requested'

    def lookups(self, request, model_admin):
            return (('requested', 'Fulfill Requested'), ('unrequested', 'Not Fulfill Requested'))

    def queryset(self, request, qs):
        fulfillment_ids = [x['order']['id'] for x in api_func('fulfill', 'fulfillment')]
        if self.value() == 'requested':
            return qs.filter(id__in=fulfillment_ids)
        if self.value() == 'unrequested':
            return qs.exclude(id__in=fulfillment_ids)


class SaleAdmin(admin.ModelAdmin):
    ordering = ('-sale_date',)
    list_display=('external_channel_id', 'sale_date', 'channel',
                  'customer_code', 'shipping_name', 'special_sale', 'paid_thru')
    list_filter = ('channel', 'paid_thru', FulfillRequested)
    search_fields = ('external_channel_id', 'channel__counterparty__name',)
    save_as = True
    actions = ['delete_model', 'queue_for_warehouse', 'queue_for_backorder']
    inlines = [
        UnitSaleInline,
        SalesTaxInline,
        ProceedsAdjustmentInline
    ]
    list_select_related = ('channel__counterparty', 'channel',)

    fieldsets = (
        ('Details', {'fields': (('channel', 'sale_date',),
                                ('external_channel_id', 'customer_code',),
                                ('paid_thru', 'checkout_id',),
                                ( 'special_sale',),
                                )
                     }),
        ('Gift Details', {'fields': (('gift_wrapping', 'gift_wrap_fee',), 'gift_message',), 'classes': ('collapse',)}),
        ('Shipping Details', {'fields': (('shipping_name', 'shipping_company'), 
                                         ('external_routing_id',),
                                         ('shipping_address1', 'shipping_address2'),
                                         ('shipping_city', 'shipping_country'), ('shipping_province', 'shipping_zip'),
                                         ('shipping_phone', 'notification_email',), ),
                              'classes': ('collapse',)}),
        ('Memo', {'fields': (('memo',)), 'classes': ('collapse',)}),
    )


    def response_change(self, request, new_object):
        "They saved a change - send signal"
        sale_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new nom tran - send signal"
        res = admin.ModelAdmin.response_add(self, request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res

    def get_actions(self, request):
        actions = super(SaleAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        try:
            for o in obj.all():
                o.delete()
        except:
            obj.delete()

    class ChooseWarehouseForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        warehouse = forms.ModelChoiceField(Warehouse.objects.all())

    
    def queue_for_warehouse(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.ChooseWarehouseForm(request.POST)
            if form.is_valid():
                warehouse = form.cleaned_data['warehouse']
                new_fulfills = 0
                dupe_fulfills = 0
                bad_warehouse = 0
                freight_fulfills = 0
                unknown_errors = 0

                for order in queryset:
                    res = fulfill.views.create_fulfill_request(warehouse.label, order.id)
                    if res == 'FULFILL_REQUESTED':
                        new_fulfills += 1
                    elif res == 'FULFILL_ALREADY_REQUESTED':
                        dupe_fulfills += 1
                    elif res == 'WAREHOUSE_NOT_RECOGNISED':
                        bad_warehouse += 1
                    elif res == 'FREIGHT_ORDER':
                        freight_fulfills += 1
                    else:
                        unknown_errors += 1

                messages.success(request, "Successfully created %d fulfill requests for warehouse %s." % (new_fulfills, warehouse))
                messages.info(request, "%d dupes were skipped." % dupe_fulfills)
                messages.warning(request, "%d had unrecognised warehouse." % bad_warehouse)
                messages.warning(request, "%d are freight shipments. Contact Ian." % freight_fulfills)
                messages.error(request, "%d unknown errors." % unknown_errors)

                return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = self.ChooseWarehouseForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render(request,
                      'admin/inventory/choose_warehouse.html',
                      {'title': u'Choose warehouse',
                       'objects': queryset,
                       'form': form,
                       'path': request.get_full_path()
                       })

    queue_for_warehouse.short_description = 'Queue for fulfillment'
    delete_model.short_description = 'Delete sales and related GL entries'

admin.site.register(Sale, SaleAdmin)



class PayoutLineInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        pass

class PayoutLineInline(admin.TabularInline):
    model = PayoutLine
    can_delete = True
    extra = 0


    def formfield_for_foreignkey(self, db_field, request=None,**kwargs):
        field = super(PayoutLineInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'sale':
            field.queryset = field.queryset.select_related('customer_code', 'channel__counterparty', 'paid_thru')
        return field

# special signal as normal GL update doesn't work with NominalTransaction
payout_tran_saved = django.dispatch.Signal(providing_args=[])
payout_tran_saved.connect(on_bmo_save)

class PayoutAdmin(admin.ModelAdmin):
    ordering = ('-payout_date',)
    list_display = ('__unicode__', 'payout_date', 'payout', 'paid_thru', 'channel',)
    list_filter = ('channel', 'paid_thru',)
    list_select_related = ('channel', 'paid_thru')
    
    inlines = [PayoutLineInline]

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        payout_tran_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new payout tran - send signal"
        payout_tran_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

    def get_queryset(self, request):
        po_model = super(PayoutAdmin, self).get_queryset(request)
        po_model = po_model.prefetch_related('payout_line').prefetch_related('payout_line__sale', 'payout_line__sale__channel')
        return po_model
    

admin.site.register(Payout, PayoutAdmin)
