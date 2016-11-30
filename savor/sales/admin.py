from django.contrib import admin, messages
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import Q

from simple_history.admin import SimpleHistoryAdmin

from .models import Channel, TaxCollector, UnitSale, Sale, SalesTax, ChannelPayouts
from accountifie.gl.bmo import on_bmo_save
from accountifie.common.api import api_func
from inventory.models import Warehouse
import fulfill.views


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


class SaleAdmin(SimpleHistoryAdmin):
    ordering = ('-sale_date',)
    list_display=('external_channel_id', 'sale_date', 'channel',
                  'customer_code', 'shipping_name', 'special_sale', 'paid_thru')
    list_filter = ('channel', 'paid_thru', FulfillRequested)
    search_fields = ('external_channel_id', 'channel__counterparty__name',)
    save_as = True
    actions = ['delete_model', 'queue_for_warehouse', 'queue_for_backorder']
    inlines = [
        UnitSaleInline,
        SalesTaxInline
    ]
    list_select_related = ('channel__counterparty', 'channel',)

    fieldsets = (
        ('Details', {'fields': (('channel', 'sale_date',),
                                ('external_channel_id', 'channel_charges',),
                                ('customer_code', 'special_sale',),
                                ( 'is_return', 'paid_thru',),
                                ('memo',),
                                )
                     }),
        ('Discount', {'fields': ('discount', 'discount_code',), 'classes': ('collapse',)}),
        ('Gift Details', {'fields': (('gift_wrapping', 'gift_wrap_fee',), 'gift_message',), 'classes': ('collapse',)}),
        ('Shipping Details', {'fields': (('shipping_charge',), ('shipping_name',), 
                                         ('shipping_company', 'external_routing_id',),
                                         ('shipping_address1'), ('shipping_address2'),
                                         ('shipping_city', 'shipping_country'), ('shipping_province', 'shipping_zip'),
                                         ('shipping_phone', 'notification_email',), ),
                              'classes': ('collapse',)})
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

    def queue_for_backorder(self, request, queryset):
        new_backorders = 0
        dupe_fulfills = 0
        unknown_errors = 0

        for order in queryset:
            res = fulfill.views.create_backorder(order.id)
            if res == 'FULFILL_BACKORDERED':
                new_backorders += 1
            elif res == 'FULFILL_ALREADY_REQUESTED':
                dupe_fulfills += 1
            else:
                unknown_errors += 1

        messages.success(request, "Successfully created %d future orders." % (new_backorders))
        messages.info(request, "%d dupes were skipped." % dupe_fulfills)
        messages.error(request, "%d unknown errors." % unknown_errors)

        return HttpResponseRedirect(request.get_full_path())


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
    queue_for_backorder.short_description = 'Add to back-order queue'
    delete_model.short_description = 'Delete sales and related GL entries'

admin.site.register(Sale, SaleAdmin)

class ChannelPayoutsAdmin(admin.ModelAdmin):
    ordering = ('-payout_date',)
    list_display = ('__unicode__', 'payout_date', 'payout', 'paid_thru', 'channel',)
    filter_horizontal = ('sales',)
    
admin.site.register(ChannelPayouts, ChannelPayoutsAdmin)

