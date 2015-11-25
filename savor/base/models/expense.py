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
import accountifie.environment.api
import accountifie._utils

logger = logging.getLogger('default')

DZERO = Decimal('0')


EASTERN = pytz.timezone('US/Eastern')

def get_changed(dt):
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)
    qs_list = [exp.history.get_queryset()[0] for exp in Expense.objects.all()]
    history = [exp.__dict__ for exp in qs_list if exp.history_user_id and exp.history_date > cutoff]

    cols = ['comment', 'last_name', 'process_date', 'id',  'first_name', 'employee_id', 'dept_name', 'company_id', 'expense_date', 
            'history_date', 'start_date', 'department_id', 'glcode', 'expense_report_name', 'vendor', 'end_date', 'history_id', 
            'approver', 'ccard', 'dept_code', 'expense_category', 'reason', 'history_type', 'reimbursable', 'counterparty_id', 
            'paid_from_id', 'e_mail', 'history_user_id', 'amount', 'processor']

    filt_history = [dict((k,str(v)) for k,v in exp.iteritems() if k in cols) for exp in history]
    return json.dumps(filt_history)


class Expense(models.Model, BusinessModelObject):
    
    company = models.ForeignKey('gl.Company', default=accountifie._utils.get_default_company)
    
    stub = models.BooleanField(default=False)
    from_cf = models.ForeignKey('base.Cashflow', null=True)

    employee = models.ForeignKey('gl.Employee', null=True)
    account = models.ForeignKey('gl.Account')
    
    expense_date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.FloatField(null=True)
    
    currency = models.CharField(max_length=10, default='USD')
    process_date = models.DateField(null=True)

    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")

    paid_from = models.ForeignKey('gl.Account', null=True, blank=True, 
        help_text="shows the account this was paid from, or is owed to",
        limit_choices_to={'id__in': [1001, 1002, 1003, 3000, 3010, 3020, 3250, 1250]
            },
        related_name='paid_from'
        )
    comment = models.CharField(max_length=200, blank=True, null=True, help_text="Details of any modifications/notes added in Django")    

    history = HistoricalRecords()

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


    def get_gl_transactions(self):
        """We just debit the expense account and credit the generic
        Accounts Payable, whoever it is.  We do not at this stage
        try to handle anything on how the debt was paid off.

        """

        capitalize_it, debit, acc_asset_dep, months  = self._capitalize(self.account)
        ACCTS_PAYABLE = accountifie.gl.models.Account.objects.get(id=accountifie.environment.api.variable({'name': 'GL_ACCOUNTS_PAYABLE'}))
        PREPAID_EXP = accountifie.gl.models.Account.objects.get(id=accountifie.environment.api.variable({'name': 'GL_PREPAID_EXP'}))
        ACCRUED_LIAB = accountifie.gl.models.Account.objects.get(id=accountifie.environment.api.variable({'name': 'GL_ACCRUED_LIAB'}))
        
        trans = []

        # now three different paths

        if capitalize_it:
            # book to asset account
            trans.append(dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'CPLZ'),
                    comment= "Capitalized Asset, %s: %s" % (self.id, self.vendor),
                    lines=[
                        (debit, Decimal(self.amount), self.counterparty),
                        (ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty),
                        ]
                    ))

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
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'DPRC'),
                    comment= "Depreciating asset,  %s: %s" % (self.id, self.vendor),
                    lines=[
                        (acc_pl_dep, DZERO - Decimal(self.amount), self.counterparty),
                        (acc_asset_dep, Decimal(self.amount), self.counterparty),
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
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'AP'),
                    comment= "AP for %s: %s" % (self.id, self.vendor),
                    lines=[
                        (PREPAID_EXP, Decimal(self.amount), self.counterparty),
                        (ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty),
                        ]
                    ))

                # expense over period
                trans.append(dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=self.end_date,
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'EXPS'),
                    comment= "Expensing %s: %s" % (self.id, self.vendor),
                    lines=[
                        (debit, Decimal(self.amount), self.counterparty),
                        (PREPAID_EXP, DZERO - Decimal(self.amount), self.counterparty),
                        ]
                    ))
            else:
                # paid in arrears
                
                # transfer from accrued liab to account payable at end of period
                trans.append(dict(
                    company=self.company,
                    date=self.end_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'AL2AP'),
                    comment= "AP for %s: %s" % (self.id, self.vendor),
                    lines=[
                        (ACCRUED_LIAB, Decimal(self.amount), self.counterparty),
                        (ACCTS_PAYABLE, DZERO - Decimal(self.amount), self.counterparty),
                        ]
                    ))

                # accrue expense over period
                trans.append(dict(
                    company=self.company,
                    date=self.start_date,
                    date_end=self.end_date,
                    trans_id='%s.%s.%s' % ('EXP', self.id, 'AL'),
                    comment= "Accruing %s: %s" % (self.id, self.vendor),
                    lines=[
                        (debit, Decimal(self.amount), self.counterparty),
                        (ACCRUED_LIAB, DZERO - Decimal(self.amount), self.counterparty),
                        ]
                    ))

        else: # single date
            trans.append(dict(
                company=self.company,
                date=self.start_date,
                date_end=None,
                trans_id='%s.%s.%s' % ('EXP', self.id, 'EXP'),
                comment= "%s" % (self.id),
                lines=[
                    (debit, float(self.amount), self.counterparty),
                    (ACCTS_PAYABLE, 0 - float(self.amount), self.counterparty),
                    ]
                ))

        return trans

class BadExpense(models.Model):
    # for Certify expenses that we want to exclude from loading
    certify_id = models.CharField(max_length=20)
    comment = models.TextField(max_length=200, null=True, blank=True)

    class Meta:
        app_label = 'base'
        db_table = 'base_badexpense'

