from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.bmo



class Cashflow(models.Model, accountifie.gl.bmo.BusinessModelObject):
    ext_account = models.ForeignKey('gl.ExternalAccount')
    post_date = models.DateField()
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.TextField(max_length=200, null=True)
    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")
    trans_type = models.ForeignKey('gl.Account', null=True, blank=True, help_text="We need to match this up")
    external_id = models.CharField(max_length=20, null=True)

    history = HistoricalRecords()

    class Meta:
        app_label = 'base'
        db_table = 'base_cashflow'

    def __unicode__(self):
        return '%.2f: %s: %s' % (self.amount, self.counterparty, self.post_date.strftime('%d-%b-%y'))

    def save(self):
        models.Model.save(self)
        if self.trans_type is not None:
            self.update_gl()

    def get_gl_transactions(self):
        credit = self.trans_type
        debit = self.ext_account.gl_account
        depositary = self.ext_account.counterparty
        
        trans = []
        trans.append(dict(
            company=self.ext_account.company,
            date=self.post_date,
            comment= "%s: %s" % (self.id, self.description[:75]),
            trans_id='%s.%s.%s' % (self.ext_account.label, self.id, 'CFLOW'),
            lines=[
                (debit, float(self.amount), depositary),
                (credit, 0 - float(self.amount), self.counterparty),
                ]
            ))
        return trans