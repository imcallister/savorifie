from django.contrib import admin
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect

from simple_history.admin import SimpleHistoryAdmin

from .models import *
from accountifie.gl.bmo import on_bmo_save
from accountifie.common.api import api_func


class UnmatchedCashflows(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED', 'MATCHED'), ('UNMATCHED', 'UNMATCHED'))

    def queryset(self, request, qs):
        if self.value() == 'UNMATCHED':
            return qs.filter(counterparty=None)
        if self.value() == 'MATCHED':
            return qs.exclude(counterparty=None)


class UnmatchedExpense(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED','MATCHED'),('UNMATCHED','UNMATCHED'))

    def queryset(self, request, qs):
        unalloc_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
        if self.value()=='UNMATCHED':
            return qs.filter(account_id=unalloc_account)
        if self.value()=='MATCHED':
            return qs.exclude(account_id=unalloc_account)


class CashflowAdmin(SimpleHistoryAdmin):
    list_display = ('ext_account', 'description', 'amount', 'post_date', 'counterparty', 'trans_type', )
    list_filter = ('ext_account', UnmatchedCashflows)
    list_editable = ('counterparty', 'trans_type',)
    search_fields = ('counterparty__id',)
    actions = ['expense_stubs_from_cashflows']

    def expense_stubs_from_cashflows(self, request, queryset):
        rslts = make_expense_stubs(queryset.values())
        self.message_user(request, "%d new stub expenses created. %d duplicates found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")

admin.site.register(Cashflow, CashflowAdmin)


class McardExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1


class McardAdmin(SimpleHistoryAdmin):
    list_display = ('company', 'id','counterparty', 'card_number', 'type', 'description', 'amount', 'post_date', 'trans_date')
    list_filter = ('type',)

admin.site.register(Mcard, McardAdmin)


class AMEXAdmin(SimpleHistoryAdmin):
    list_display = ('company', 'id','counterparty', 'description', 'amount', 'date',)
admin.site.register(AMEX, AMEXAdmin)


class ExpenseAdmin(SimpleHistoryAdmin):
    ordering = ('-expense_date',)
    actions = ['delete_model']
    list_display = ('id', 'account','expense_date','paid_from', 'comment', 'counterparty', 'employee','currency','amount',)
    list_filter = ('expense_date', 'employee', 'paid_from', UnmatchedExpense)
    search_fields = ['id','counterparty__id', 'account__id']
    list_editable = ('employee', 'account', 'paid_from', 'comment')


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
    list_display = ('counterparty',)
    list_filter = ('counterparty',)

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
    list_display=('external_channel_id', 'sale_date', 'channel', 'customer_code', 'shipping_name', 'shipping_code',)
    list_filter = ('channel', FulfillRequested)
    search_fields = ('external_channel_id', 'channel__counterparty__name',)
    save_as = True
    actions = ['delete_model']
    inlines = [
        UnitSaleInline,
        SalesTaxInline
    ]

    fieldsets = (
        ('Details', {'fields': (('channel', 'sale_date',), ('customer_code',), ('memo',),)}),
        ('External IDs', {'fields': (('external_ref', 'external_routing_id'), ('external_channel_id',)), 'classes': ('collapse',)}),
        ('Discount', {'fields': ('discount', 'discount_code',), 'classes': ('collapse',)}),
        ('Gift Details', {'fields': (('gift_wrapping', 'gift_wrap_fee',), 'gift_message',), 'classes': ('collapse',)}),
        ('Shipping Details', {'fields': (('shipping_charge',), ('shipping_name',), ('shipping_company',),
                                         ('shipping_address1'), ('shipping_address2'),
                                         ('shipping_city', 'shipping_country'), ('shipping_province', 'shipping_zip'),
                                         ('shipping_phone', 'notification_email',), ('shipping_code', 'shipping_type',)),
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
    
    delete_model.short_description = 'Delete sales and related GL entries'

admin.site.register(Sale, SaleAdmin)
