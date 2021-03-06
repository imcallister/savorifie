from decimal import Decimal

from django.db import models
from django.http import HttpResponseRedirect

import accountifie.gl.bmo

DZERO = Decimal('0')

CASHFLOW_TRANSTYPE_CHOICES = ['1002', '1100', '1250', '3000', '1500', '7090', '3510', '3005', '3006']

class CashflowAllocation(models.Model):
    cashflow = models.ForeignKey('base.Cashflow')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")
    trans_type = models.ForeignKey('gl.Account', null=True, blank=True, help_text="We need to match this up")
    project = models.ForeignKey('gl.Project', null=True, blank=True)
    tag = models.CharField(max_length=30, null=True, blank=True)
    
    class Meta:
        app_label = 'base'
        db_table = 'base_cashflowallocation'

    def __unicode__(self):
        return '%.2f, C/P %s, project %s, tag %s' %(self.amount, self.counterparty, self.project, self.tag)



class Cashflow(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default='SAV')
    ext_account = models.ForeignKey('gl.ExternalAccount')
    post_date = models.DateField()
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.TextField(max_length=200, null=True)
    external_id = models.CharField(max_length=20, null=True)
    trans_type = models.ForeignKey('gl.Account', null=True, 
                                    blank=True, help_text="We need to match this up",
                                    limit_choices_to={'id__in': CASHFLOW_TRANSTYPE_CHOICES})
    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")
    expense_acct = models.ForeignKey('gl.Account', null=True, blank=True,
                                     related_name='expense_acct',
                                     help_text='Optional. For related expense created from Credit Card Trans')

    tag = models.CharField(max_length=30, null=True, blank=True)
    
    short_code = 'CFLOW'

    class Meta:
        app_label = 'base'
        db_table = 'base_cashflow'

    def __unicode__(self):
        return '%.2f: %s: %s' % (self.amount, self.external_id, self.post_date.strftime('%d-%b-%y'))

    def save(self, update_gl=True):
        models.Model.save(self)
        if update_gl:
            self.update_gl()

    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)
    
    def _get_alloc_lines(self):
        allocations = self.cashflowallocation_set.all()
        
        alloc_lines = []
        running_total = DZERO
        if len(allocations) > 0:
            for allocation in allocations:
                if allocation.project is None:
                    tags = []
                else:
                    tags = ['project_%s' % allocation.project.id]

                alloc_lines.append((allocation.trans_type, DZERO - Decimal(allocation.amount), allocation.counterparty, tags))
                running_total += Decimal(allocation.amount)

        if abs(Decimal(self.amount) - running_total) >= Decimal('0.005'):
            alloc_lines.append((self.ext_account.gl_account, DZERO - (Decimal(self.amount) - running_total), None, []))
        
        return alloc_lines


    def get_gl_transactions(self):

        cf_acct = self.ext_account.gl_account.id
        tran = []

        tran = dict(company=self.ext_account.company,
                    date=self.post_date,
                    comment= "%s: %s" % (self.id, self.description[:75]),
                    trans_id='%s.%s.%s' % (self.short_code, self.id, self.ext_account.label),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    lines=[(cf_acct, Decimal(self.amount), self.counterparty.id, []),
                            (self.trans_type.id, -Decimal(self.amount), self.counterparty.id, [self.tag] if self.tag else [])]
                    )

        #tran['lines'] += self._get_alloc_lines()
        trans = [tran]
        
        return trans