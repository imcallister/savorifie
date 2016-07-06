from django.contrib import admin, messages
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django_bootstrap_typeahead.fields import *
from django.db.models import Q
from django.db.models import Prefetch

from simple_history.admin import SimpleHistoryAdmin

from .models import *
import accountifie.gl.widgets
from accountifie.gl.bmo import on_bmo_save
from accountifie.common.api import api_func
from inventory.models import Warehouse
import inventory.views


class UnmatchedCashflows(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED', 'MATCHED'), ('UNMATCHED', 'UNMATCHED'))

    def queryset(self, request, qs):
        if self.value() == 'UNMATCHED':
            return qs.filter(Q(counterparty=None) | Q(counterparty_id='unknown'))
        if self.value() == 'MATCHED':
            return qs.exclude(Q(counterparty=None) | Q(counterparty_id='unknown'))


class UnmatchedExpense(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED','MATCHED'),('UNMATCHED','UNMATCHED'))

    def queryset(self, request, qs):
        unalloc_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
        if self.value() == 'UNMATCHED':
            return qs.filter(account_id=unalloc_account)
        if self.value() == 'MATCHED':
            return qs.exclude(account_id=unalloc_account)


class CashflowTAForm(forms.ModelForm):
    counterparty = TypeaheadField(queryset=accountifie.gl.models.Counterparty.objects.all())

    def __init__(self, *args, **kwargs):
        super(CashflowTAForm, self).__init__(*args, **kwargs)
        rel = Cashflow._meta.get_field('counterparty').rel
        self.fields['counterparty'].widget = RelatedFieldWidgetWrapper(self.fields['counterparty'].widget, 
                                                                       rel, 
                                                                       admin.site)
    class Meta:
        model = Cashflow
        fields = ('__all__')


class CashflowDALForm(forms.ModelForm):
    counterparty = accountifie.gl.widgets.counterparty_widget()

    def __init__(self, *args, **kwargs):
        super(CashflowDALForm, self).__init__(*args, **kwargs)
        rel = Cashflow._meta.get_field('counterparty').rel
        self.fields['counterparty'].widget = RelatedFieldWidgetWrapper(self.fields['counterparty'].widget, 
                                                                       rel,
                                                                       admin.site)

    class Meta:
        model = Cashflow
        fields = ('__all__')


class CashflowAdmin(SimpleHistoryAdmin):
    list_display = ('ext_account', 'description', 'amount', 'post_date', 'counterparty', 'trans_type', )
    list_filter = ('ext_account', UnmatchedCashflows)
    list_editable = ('counterparty', 'trans_type',)
    search_fields = ('counterparty__id',)
    actions = ['expense_stubs_from_cashflows']

    form = CashflowDALForm

    def get_queryset(self, request):
        return super(CashflowAdmin, self).get_queryset(request)\
                                         .select_related('company',
                                                         'ext_account', 
                                                         'counterparty__name',
                                                         'trans_type',
                                                         )

    def get_changelist_form(self, request, **kwargs):
        return self.form

    def expense_stubs_from_cashflows(self, request, queryset):
        rslts = make_expense_stubs(queryset.values())
        self.message_user(request, "%d new stub expenses created. %d duplicates found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")

admin.site.register(Cashflow, CashflowAdmin)


class CreditCardTransTAForm(forms.ModelForm):
    counterparty = TypeaheadField(queryset=accountifie.gl.models.Counterparty.objects.all())

    def __init__(self, *args, **kwargs):
        super(CreditCardTransTAForm, self).__init__(*args, **kwargs)
        rel = CreditCardTrans._meta.get_field('counterparty').rel
        self.fields['counterparty'].widget = RelatedFieldWidgetWrapper(self.fields['counterparty'].widget, 
                                                                       rel, 
                                                                       admin.site)
    class Meta:
        model = CreditCardTrans
        fields = ('__all__')


class CreditCardTransDALForm(forms.ModelForm):
    counterparty = accountifie.gl.widgets.counterparty_widget()

    def __init__(self, *args, **kwargs):
        super(CreditCardTransDALForm, self).__init__(*args, **kwargs)
        rel = CreditCardTrans._meta.get_field('counterparty').rel
        self.fields['counterparty'].widget = RelatedFieldWidgetWrapper(self.fields['counterparty'].widget, 
                                                                       rel, 
                                                                       admin.site)
    class Meta:
        model = CreditCardTrans
        fields = ('__all__')


class CreditCardTransAdmin(SimpleHistoryAdmin):
    ordering = ('-trans_date',)
    list_editable = ('counterparty', 'expense_acct',)
    list_display = ('trans_id', 'card_company', 'trans_date', 'post_date',
                    'trans_type', 'amount', 'payee', 'counterparty', 
                    'card_number', 'expense_acct',)
    list_filter = ('card_number', 'trans_type', UnmatchedCashflows)
    search_fields = ['trans_id', 'counterparty__id',]
    actions = ['expense_stubs_from_ccard']

    form = CreditCardTransDALForm

    def get_changelist_form(self, request, **kwargs):
        return self.form

    def expense_stubs_from_ccard(self, request, queryset):
        rslts = make_stubs_from_ccard(queryset.values())
        self.message_user(request, "%d new stub expenses created. %d duplicates \
                                   found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")


admin.site.register(CreditCardTrans, CreditCardTransAdmin)

class ExpenseTAForm(forms.ModelForm):
    account = TypeaheadField(queryset=accountifie.gl.models.Account.objects.all())

    def __init__(self, *args, **kwargs):
        super(ExpenseTAForm, self).__init__(*args, **kwargs)
        rel = Expense._meta.get_field('account').rel
        self.fields['account'].widget = RelatedFieldWidgetWrapper(self.fields['account'].widget, 
                                                                       rel, 
                                                                       admin.site)
    class Meta:
        model = Expense
        fields = ('__all__')


class ExpenseDALForm(forms.ModelForm):
    account = accountifie.gl.widgets.account_widget()

    def __init__(self, *args, **kwargs):
        super(ExpenseDALForm, self).__init__(*args, **kwargs)
        rel = Expense._meta.get_field('account').rel
        self.fields['account'].widget = RelatedFieldWidgetWrapper(self.fields['account'].widget, 
                                                                  rel,
                                                                  admin.site)

    class Meta:
        model = Expense
        fields = ('__all__')


class ExpenseAdmin(SimpleHistoryAdmin):
    ordering = ('-expense_date',)
    actions = ['delete_model']
    list_display = ('id', 'account', 'expense_date', 'comment',
                    'counterparty', 'amount',)
    list_filter = ('expense_date', 'employee', 'paid_from', UnmatchedExpense)
    search_fields = ['id', 'counterparty__id', 'account__id']
    list_editable = ('account', 'comment', 'counterparty',)

    form = ExpenseDALForm

    def get_changelist_form(self, request, **kwargs):
        return self.form

    def get_actions(self, request):
        actions = super(ExpenseAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        try:
            for o in obj.all():
                o.delete()
        except:
            obj.delete()
    delete_model.short_description = 'Delete expense and related GL entries'


admin.site.register(Expense, ExpenseAdmin)


class StockEntryAdmin(SimpleHistoryAdmin):
    list_display = ('date', 'quantity','share_class', 'gl_acct',)
    list_filter = ('share_class', 'gl_acct',)
    search_fields = ('date', 'quantity','share_class', 'gl_acct',)

admin.site.register(StockEntry, StockEntryAdmin)


# special signal as normal GL update doesn't work with NominalTransaction
nom_tran_saved = django.dispatch.Signal(providing_args=[])
nom_tran_saved.connect(on_bmo_save)


class NominalInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        count = 0
        balance = DZERO
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    count += 1
                    balance += form.cleaned_data["amount"]
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError('You must have at least one line')
        if balance != DZERO:
            raise forms.ValidationError('Out by %s' % balance)


class NominalTranLineInline(admin.TabularInline):
    model = NominalTranLine  
    formset = NominalInlineFormset


class NominalTransactionAdmin(SimpleHistoryAdmin):
    list_display=('company', 'id', 'date',  'comment')
    list_filter = ('company',)
    search_fields = ('comment','id')
    ordering = ('-date','id')
    save_as = True
    save_on_top = True
    inlines = [
        NominalTranLineInline,
    ]

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        nom_tran_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new nom tran - send signal"
        nom_tran_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(NominalTransaction, NominalTransactionAdmin)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('label', 'counterparty',)
    list_filter = ('label', 'counterparty',)

admin.site.register(Channel, ChannelAdmin)


class TaxCollectorAdmin(admin.ModelAdmin):
    list_display = ('entity',)
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
        fulfillment_ids = [x['order_id'] for x in api_func('inventory', 'fulfillment')]
        if self.value() == 'requested':
            return qs.filter(id__in=fulfillment_ids)
        if self.value() == 'unrequested':
            return qs.exclude(id__in=fulfillment_ids)


class SaleAdmin(SimpleHistoryAdmin):
    list_display=('external_channel_id', 'external_ref', 'sale_date', 'channel',
                  'customer_code', 'shipping_name', 'ship_type',)
    list_filter = ('channel', FulfillRequested)
    search_fields = ('external_channel_id', 'channel__counterparty__name',)
    save_as = True
    actions = ['delete_model', 'queue_for_warehouse']
    inlines = [
        UnitSaleInline,
        SalesTaxInline
    ]
    list_select_related = ('channel__counterparty', 'channel',)

    fieldsets = (
        ('Details', {'fields': (('channel', 'sale_date',),
                                ('external_channel_id', 'external_ref',),
                                ('customer_code', 'special_sale'),
                                ('memo',),
                                )
        }),
        ('Discount', {'fields': ('discount', 'discount_code',), 'classes': ('collapse',)}),
        ('Gift Details', {'fields': (('gift_wrapping', 'gift_wrap_fee',), 'gift_message',), 'classes': ('collapse',)}),
        ('Shipping Details', {'fields': (('shipping_charge',), ('shipping_name',), 
                                         ('shipping_company', 'external_routing_id',),
                                         ('shipping_address1'), ('shipping_address2'),
                                         ('shipping_city', 'shipping_country'), ('shipping_province', 'shipping_zip'),
                                         ('shipping_phone', 'notification_email',), ('ship_type',)),
                              'classes': ('collapse',)})
    )

    
    """
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        return super(SaleAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)
    """


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
                unknown_errors = 0

                for order in queryset:
                    res = inventory.views.create_fulfill_request(warehouse.label, order.id)
                    if res == 'FULFILL_REQUESTED':
                        new_fulfills += 1
                    elif res == 'FULFILL_ALREADY_REQUESTED':
                        dupe_fulfills += 1
                    elif res == 'WAREHOUSE_NOT_RECOGNISED':
                        bad_warehouse += 1
                    else:
                        unknown_errors += 1

                messages.success(request, "Successfully created %d fulfill requests for warehouse %s." % (new_fulfills, warehouse))
                messages.info(request, "%d dupes were skipped." % dupe_fulfills)
                messages.warning(request, "%d had unrecognised warehouse." % bad_warehouse)
                messages.error(request, "%d unknown errors." % unknown_errors)

                return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = self.ChooseWarehouseForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render_to_response('admin/inventory/choose_warehouse.html',
                                    {'title': u'Choose warehouse',
                                     'objects': queryset,
                                     'form': form,
                                     'path': request.get_full_path()
                                     },
                                    context_instance=RequestContext(request))


        
    queue_for_warehouse.short_description = 'Queue for fulfillment'
    delete_model.short_description = 'Delete sales and related GL entries'

admin.site.register(Sale, SaleAdmin)
