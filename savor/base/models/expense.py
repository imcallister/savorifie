import pytz
import json
import datetime
import logging

from django.db import models
from django.utils.safestring import mark_safe
from django.conf import settings

from decimal import Decimal
from simple_history.models import HistoricalRecords
from dateutil.relativedelta import relativedelta

from accountifie.gl.bmo import BusinessModelObject
import accountifie.gl.models
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func

logger = logging.getLogger('default')

DZERO = Decimal('0')
EASTERN = pytz.timezone('US/Eastern')




def make_expense_stubs(cf_data):
    """
    given a list of cashflows create expenses
    from those cashflows which have not already had an expense created from them
    where the cashflows were booked versus Accounts Payable
    """
    today = datetime.datetime.now().date()
    stub_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
    unallocated_employee = api_func('environment', 'variable', 'UNALLOCATED_EMPLOYEE_ID')
    ap_account = api_func('environment', 'variable', 'GL_ACCOUNTS_PAYABLE')

    new_stubs = 0
    from_AP = [cf for cf in cf_data if cf['trans_type_id'] == ap_account]
    for cf in from_AP:
        if Expense.objects.filter(from_cf_id=cf['id']).count() == 0:
            new_stubs += 1

            # if expense acct is on the cashflow then use that
            if cf['expense_acct_id']:
                account_id = cf['expense_acct_id']
            else:
                account_id = stub_account

            Expense(comment=cf['description'], counterparty_id=cf['counterparty_id'], account_id=account_id, from_cf_id=cf['id'],
                    expense_date=cf['post_date'], start_date=cf['post_date'], amount=-cf['amount'], stub=False,
                    paid_from_id=cf['trans_type_id'], process_date=today, employee_id=unallocated_employee).save()

    return {'new': new_stubs, 'duplicates': len(from_AP) - new_stubs}


def make_stubs_from_ccard(cc_data):
    """
    given a list of credit card transactions create expenses
    from those credit card trans which have not already had 
    an expense created from them
    """
    today = datetime.datetime.now().date()
    stub_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
    unallocated_employee = api_func('environment', 'variable', 'UNALLOCATED_EMPLOYEE_ID')
    ap_account = api_func('environment', 'variable', 'GL_ACCOUNTS_PAYABLE')

    new_stubs = 0
    for cc in cc_data:
        if Expense.objects.filter(from_ccard_id=cc['id']).count()==0:
            new_stubs += 1

            # if expense acct is on the cashflow then use that
            if cc['expense_acct_id']:
                account_id = cc['expense_acct_id']
            else:
                account_id = stub_account

            Expense(comment=cc['description'], counterparty_id=cc['counterparty_id'],
                    account_id=stub_account, from_ccard_id=cc['id'],
                    expense_date=cc['trans_date'], start_date=cc['post_date'],
                    amount=-cc['amount'], stub=False, paid_from_id=ap_account,
                    process_date=today, employee_id=unallocated_employee).save()

    return {'new': new_stubs, 'duplicates': len(cc_data) - new_stubs}


def get_changed(dt):
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)
    qs_list = [exp.history.get_queryset()[0] for exp in Expense.objects.all()]
    history = [exp.__dict__ for exp in qs_list if exp.history_user_id and exp.history_date > cutoff]

    cols = ['comment', 'last_name', 'process_date', 'id', 'first_name',
            'employee_id', 'dept_name', 'company_id', 'expense_date',
            'history_date', 'start_date', 'department_id', 'glcode',
            'expense_report_name', 'vendor', 'end_date', 'history_id',
            'approver', 'ccard', 'dept_code', 'expense_category', 'reason',
            'history_type', 'reimbursable', 'counterparty_id',
            'paid_from_id', 'e_mail', 'history_user_id', 'amount', 'processor']

    filt_history = [dict((k,str(v)) for k,v in exp.iteritems() if k in cols) for exp in history]
    return json.dumps(filt_history)

class ExpenseAllocation(models.Model):
    expense = models.ForeignKey('base.Expense')
    project = models.ForeignKey('gl.Project')
    amount = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'base'
        db_table = 'base_expenseallocation'

    def __unicode__(self):
        return '%.2f: Project %s' %(self.amount, self.project)


class Expense(models.Model, BusinessModelObject):
    
    company = models.ForeignKey('gl.Company', default=get_default_company)
    
    employee = models.ForeignKey('gl.Employee', null=True)
    account = models.ForeignKey('gl.Account')
    
    expense_date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    
    currency = models.CharField(max_length=10, default='USD')
    process_date = models.DateField(null=True)

    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")
    
    stub = models.BooleanField(default=False, help_text='incomplete, created from cashflow or credit card')
    from_cf = models.ForeignKey('base.Cashflow', null=True, blank=True, 
                                help_text='created from cashflow')
    from_ccard = models.ForeignKey('base.CreditCardTrans', null=True, blank=True,
                                   help_text='created from credit card trans')

    paid_from = models.ForeignKey('gl.Account', null=True, blank=True,
                                  help_text="shows the account this was paid from, or is owed to",
                                  limit_choices_to={'id__in': [1001, 1002, 1003, 3000, 3010, 3020, 3250, 20100]},
                                  related_name='paid_from')
    comment = models.CharField(max_length=200, blank=True, null=True, help_text="Details of any modifications/notes added in Django")    

    history = HistoricalRecords()
    short_code = 'EXP'

    class Meta:
        app_label = 'base'
        db_table = 'base_expense'

    def __unicode__(self):
        return '%d: %s: %s, %0.2f' % (self.id, self.expense_date.isoformat(), self.counterparty, self.amount)

    def save(self):
        models.Model.save(self)
        if not self.stub:
            self.update_gl()
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    @property
    def counterparty_name(self):
        return self.counterparty.name

    @property
    def amount_fmt(self):
        return "{:,.0f}".format(self.amount)

    @property
    def id_link(self):
        return mark_safe('<a href="/base/expense/%s">%s' %( self.id, self.id))

    @property
    def admin_link(self):
        return mark_safe('<a href="/admin/base/expense/%s">admin %s' %( self.id, self.id))

    def _capitalize(self, debit):
        # capitalising or not
        all_deprec_accts = dict((x.cap_account, x) for x in accountifie.gl.models.DepreciationPolicy.objects.all())
        capitalize_it =  (debit in all_deprec_accts and abs(self.amount) >= 500.0)
        expense_it = (debit in all_deprec_accts and abs(self.amount) < 500.0)

        acc_asset_dep = None
        months = None
        if expense_it:
            exp_path = debit.path.replace('assets.noncurr.premandequip', 'equity.retearnings.opexp.admin')
            debit = accountifie.gl.models.Account.objects.filter(path=exp_path)[0]      
        elif capitalize_it:
            acc_asset_dep = all_deprec_accts[debit].depreciation_account
            months = all_deprec_accts[debit].depreciation_period
        return capitalize_it, debit, acc_asset_dep, months 


    def _get_exp_lines(self, exp_acct):
        #allocations = self.expenseallocation_set.all()
        allocations = ExpenseAllocation.objects.filter(expense=self)
        exp_lines = []
        running_total = DZERO
        if len(allocations) > 0:
            for allocation in allocations:
                exp_lines.append((exp_acct, Decimal(allocation.amount), self.counterparty, ['project_%s' % allocation.project.id]))
                running_total += Decimal(allocation.amount)

        if abs(Decimal(self.amount) - running_total) >= Decimal('0.005'):
            exp_lines.append((exp_acct, Decimal(self.amount) - running_total, self.counterparty, []))
        
        return exp_lines


    def get_gl_transactions(self):
        """We just debit the expense account and credit the generic
        Accounts Payable, whoever it is.  We do not at this stage
        try to handle anything on how the debt was paid off.

        """

        capitalize_it, debit, acc_asset_dep, months  = self._capitalize(self.account)
        ACCTS_PAYABLE = accountifie.gl.models.Account.objects.get(id=api_func('environment', 'variable', 'GL_ACCOUNTS_PAYABLE'))
        PREPAID_EXP = accountifie.gl.models.Account.objects.get(id=api_func('environment', 'variable', 'GL_PREPAID_EXP'))
        ACCRUED_LIAB = accountifie.gl.models.Account.objects.get(id=api_func('environment', 'variable', 'GL_ACCRUED_LIAB'))
        
        trans = []

        # now three different paths

        if capitalize_it:
            # book to asset account
            tran = dict(
                        company=self.company,
                        date=self.start_date,
                        date_end=None,
                        trans_id='%s.%s.%s' % (self.short_code, self.id, 'CPLZ'),
                        bmo_id='%s.%s' % (self.short_code, self.id),
                        comment= "Capitalized Asset, %s: %s" % (self.id, self.comment),
                        lines=[(ACCTS_PAYABLE,
                                DZERO - Decimal(self.amount),
                                self.counterparty,
                                [])]
                    )

            tran['lines'] += self._get_exp_lines(debit)
            trans.append(tran)
            # and now amort/deprec over appropriate time period

            amort_accts = accountifie.gl.models.Account.objects.filter(path=debit.path + '.amortization')
            if len(amort_accts) > 0:
                acc_pl_dep = amort_accts[0]

            deprec_accts = accountifie.gl.models.Account.objects.filter(path=debit.path + '.depreciation')
            if len(deprec_accts) > 0:
                acc_pl_dep = deprec_accts[0]

            trans.append(dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=self.start_date + relativedelta(months=months),
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'DPRC'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    comment= "Depreciating asset,  %s: %s" % (self.id, self.comment),
                    lines=[
                        (acc_pl_dep, DZERO - Decimal(self.amount), self.counterparty, []),
                        (acc_asset_dep, Decimal(self.amount), self.counterparty, []),
                        ]
                    ))

        elif self.end_date is not None and self.start_date != self.end_date and abs(self.amount) >=500.0:

            if self.expense_date == self.start_date:
                # paid in advance
                # create account payable
                trans.append(dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'AP'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    comment= "AP for %s: %s" % (self.id, self.comment),
                    lines=[
                        (PREPAID_EXP, Decimal(self.amount), self.counterparty, []),
                        (ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty, []),
                        ]
                    ))

                # expense over period
                tran = dict(
                            company=self.company,
                            date=self.start_date,
                            date_end=self.end_date,
                            trans_id='%s.%s.%s' % (self.short_code, self.id, 'EXPS'),
                            bmo_id=self.id,
                            comment= "Expensing %s: %s" % (self.id, self.comment),
                            lines=[(PREPAID_EXP, DZERO - Decimal(self.amount), self.counterparty, []),]
                        )
                tran['lines'] += self._get_exp_lines(debit)
                trans.append(tran)
            else:
                # paid in arrears
                
                # transfer from accrued liab to account payable at end of period
                trans.append(dict(
                    company=self.company,
                    date=self.end_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'AL2AP'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    comment= "AP for %s: %s" % (self.id, self.comment),
                    lines=[
                        (ACCRUED_LIAB, Decimal(self.amount), self.counterparty, []),
                        (ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty, []),
                        ]
                    ))

                # accrue expense over period
                tran = dict(
                            company=self.company,
                            date=self.start_date,
                            date_end=self.end_date,
                            trans_id='%s.%s.%s' % (self.short_code, self.id, 'AL'),
                            bmo_id='%s.%s' % (self.short_code, self.id),
                            comment= "Accruing %s: %s" % (self.id, self.comment),
                            lines=[(ACCRUED_LIAB, DZERO - Decimal(self.amount), self.counterparty, []),]
                        )
                
                tran['lines'] += self._get_exp_lines(debit)
                trans.append(tran)

        else: # single date
            tran = dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'EXP'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    comment= "%s: %s" % (self.id, self.comment),
                    lines=[(ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty, []),]
                )

            tran['lines'] += self._get_exp_lines(debit)
            trans.append(tran)

        return trans