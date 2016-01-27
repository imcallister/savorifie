from django.contrib import admin
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter


from simple_history.admin import SimpleHistoryAdmin

from .models import *
from accountifie.gl.bmo import on_bmo_save
from accountifie.gl.models import Account




class UnmatchedCashflows(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED','MATCHED'),('UNMATCHED','UNMATCHED'))

    def queryset(self, request, qs):
        if self.value()=='UNMATCHED':
            return qs.filter(counterparty=None)
        if self.value()=='MATCHED':
            return qs.exclude(counterparty=None)

class UnmatchedExpense(SimpleListFilter):
    title = 'unmatched'
    parameter_name = 'unmatched'

    def lookups(self, request, model_admin):
            return (('MATCHED','MATCHED'),('UNMATCHED','UNMATCHED'))

    def queryset(self, request, qs):
        if self.value()=='UNMATCHED':
            return qs.filter(stub=True)
        if self.value()=='MATCHED':
            return qs.exclude(stub=False)


class CashflowAdmin(SimpleHistoryAdmin):
    list_display = ('ext_account', 'description', 'amount', 'post_date', 'counterparty', 'trans_type', )
    list_filter = ('ext_account', UnmatchedCashflows)
    list_editable = ('counterparty', 'trans_type',)
    search_fields = ('counterparty__id',)
    actions = ['make_expense_stubs']

    def make_expense_stubs(self, request, queryset):
        stub_account = accountifie.environment.api.variable({'name': 'UNALLOCATED_ACCT'})
        new_stubs = 0
        from_AP = queryset.filter(trans_type__id=accountifie.environment.api.variable({'name': 'GL_ACCOUNTS_PAYABLE'}))
        for cf in from_AP.all():
            if Expense.objects.filter(from_cf=cf).count()==0:
                new_stubs += 1
                Expense(comment=cf.description, counterparty=cf.counterparty, account_id=stub_account, from_cf=cf,
                        expense_date=cf.post_date, start_date=cf.post_date, amount=-cf.amount, stub=True).save()
        self.message_user(request, "%d new stub expenses created. %d duplicates found and not created" % (new_stubs, from_AP.count()-new_stubs))
        

admin.site.register(Cashflow, CashflowAdmin)   


"""
class MastercardPaysExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'expense', 'carditem', 'amount']
    ordering = ['expense__expense_date']
admin.site.register(McardPaysExpense, MastercardPaysExpenseAdmin)
"""

class McardExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1


class McardAdmin(SimpleHistoryAdmin):
    list_display = ('company', 'id','counterparty', 'card_number', 'type', 'description', 'amount', 'post_date', 'trans_date')
    list_filter = ('type',)
    #inlines = [McardExpenseInline]  - wrong, or needs Django 1.7?

admin.site.register(Mcard, McardAdmin)

class AMEXAdmin(SimpleHistoryAdmin):
    list_display = ('company', 'id','counterparty', 'description', 'amount', 'date',)
    #inlines = [McardExpenseInline]  - wrong, or needs Django 1.7?
admin.site.register(AMEX, AMEXAdmin)



class ExpenseAdmin(SimpleHistoryAdmin):
    ordering = ('-expense_date',)
    actions = ['delete_model']
    list_display = ('id', 'account','expense_date','paid_from', 'comment', 'counterparty', 'employee','currency','amount',)
    list_filter = ('expense_date', 'employee', 'paid_from', UnmatchedExpense)
    search_fields = ['expense_category', 'reason', 'employee__employee_name','id','counterparty__id']
    list_editable = ('employee', 'account', 'paid_from', 'comment')
    #inlines = [McardExpenseInline]  - wrong, or needs Django 1.7?

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



#special signal as normal GL update doesn't work with NominalTransaction
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


class ProductAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'description')
    search_fields = ('short_code',)



class TaxCollectorAdmin(admin.ModelAdmin):
    list_display = ('entity',)
    list_editable = ('entity',)
    search_fields = ('entity',)



admin.site.register(TaxCollector, TaxCollectorAdmin)
admin.site.register(Product, ProductAdmin)


#special signal as normal GL update doesn't work with NominalTransaction
sale_saved = django.dispatch.Signal(providing_args=[])
sale_saved.connect(on_bmo_save)


class UnitSaleInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        pass

class UnitSaleInline(admin.TabularInline):
    model = UnitSale
    can_delete = True
    extra = 0
    #formset = UnitSaleInlineFormset
    
     
    
class SalesTaxInline(admin.TabularInline):
    model = SalesTax
    can_delete = True
    extra = 0

class SaleAdmin(SimpleHistoryAdmin):
    list_display=('external_ref', 'sale_date', 'channel', 'customer_code',  'fulfill_status', 'discount_code',)
    list_filter = ('channel','fulfill_status',)
    search_fields = ('external_ref', 'channel','fulfill_status',)
    save_as = True
    inlines = [
        UnitSaleInline,
        SalesTaxInline
        ]

    fieldsets = (
        ('Order Details', {'fields': (('channel', 'sale_date'), ('customer_code', 'external_ref',), ('memo', 'fulfill_status',), ('shipping', ))}),
        ('Discount', {'fields': (('discount', 'discount_code',), )}),
    )

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        sale_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new nom tran - send signal"
        sale_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(Sale, SaleAdmin)
