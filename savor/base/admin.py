from django.contrib import admin
import django.dispatch
from django import forms
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import Q


from .models import *
import accountifie.gl.widgets
from accountifie.gl.bmo import on_bmo_save
import accountifie.environment.apiv1 as env_api



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
        unalloc_account = env_api.variable('UNALLOCATED_ACCT', {})
        if self.value() == 'UNMATCHED':
            return qs.filter(account_id=unalloc_account)
        if self.value() == 'MATCHED':
            return qs.exclude(account_id=unalloc_account)


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



class CashflowAdmin(admin.ModelAdmin):
    ordering = ('-post_date',)

    list_display = ('ext_account', 'description', 'amount', 'post_date', 'counterparty',
                    'trans_type', 'expense_acct')
    list_filter = ('ext_account', UnmatchedCashflows)
    #list_editable = ('counterparty', 'trans_type', 'expense_acct')
    search_fields = ('counterparty__id',)
    actions = ['expense_stubs_from_cashflows']
    list_select_related = ('company', 'ext_account', 'counterparty', 'trans_type', 'expense_acct')

    #form = CashflowDALForm

    def get_queryset(self, request):
        return super(CashflowAdmin, self).get_queryset(request)\
                                         .select_related('company',
                                                         'ext_account', 
                                                         'counterparty',
                                                         'trans_type',
                                                         'expense_acct'
                                                         )

    #def get_changelist_form(self, request, **kwargs):
    #    return self.form

    def expense_stubs_from_cashflows(self, request, queryset):
        rslts = make_expense_stubs(queryset.values())
        self.message_user(request, "%d new stub expenses created. %d duplicates found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")

admin.site.register(Cashflow, CashflowAdmin)


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


class CreditCardTransAdmin(admin.ModelAdmin):
    ordering = ('-trans_date',)
    #list_editable = ('counterparty', 'acct_payable', 'expense_acct',)
    list_display = ('trans_id', 'card_company', 'trans_date',
                    'amount', 'payee', 'counterparty', 
                    'acct_payable', 'expense_acct',)
    list_filter = ('card_number', 'trans_type', UnmatchedCashflows)
    search_fields = ['trans_id', 'counterparty__id',]
    actions = ['expense_stubs_from_ccard']
    list_select_related = ('company', 'card_company', 'counterparty', 'acct_payable', 'expense_acct')

    #form = CreditCardTransDALForm

    #def get_changelist_form(self, request, **kwargs):
    #    return self.form

    def expense_stubs_from_ccard(self, request, queryset):
        rslts = make_stubs_from_ccard(queryset.values())
        self.message_user(request, "%d new stub expenses created. %d duplicates \
                                   found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")


admin.site.register(CreditCardTrans, CreditCardTransAdmin)


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


class ExpenseAdmin(admin.ModelAdmin):
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


class StockEntryAdmin(admin.ModelAdmin):
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


class NominalTransactionAdmin(admin.ModelAdmin):
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

