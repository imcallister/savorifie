from django.db import models


from simple_history.models import HistoricalRecords

import accountifie.gl.models
from accountifie.gl.bmo import BusinessModelObject
import accountifie._utils
import accountifie.environment.api


class Mcard(models.Model, BusinessModelObject):
    # note that this is only for charges, not for payments
    company = models.ForeignKey('gl.Company', default=accountifie._utils.get_default_company)

    trans_date = models.DateField()
    post_date = models.DateField()
    type = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    #expenses = models.ManyToManyField(Expense, through='McardPaysExpense')

    #These fields are added by our system or by a human
    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")

    history = HistoricalRecords()
    short_code = 'MCARD'

    def __unicode__(self):
        return '%s: %s: %s' % (self.id, self.trans_date.isoformat(), self.counterparty)

    class Meta:
        app_label = 'base'
        verbose_name = "Mastercard Transaction"
        verbose_name_plural = "Mastercard Transactions"
        db_table = 'base_mcard'

    def save(self):
        models.Model.save(self)
        if self.type in ['Sale', 'Adjustment', 'Fee', 'Return']:
            self.update_gl()
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    def get_gl_transactions(self):
        mcard = accountifie.gl.models.Counterparty.objects.get(id='mastercard')
        debit = accountifie.gl.models.Account.objects.get(display_name='Mastercard')
        if self.type == 'Fee':
            credit = accountifie.gl.models.Account.objects.get(display_name='Banks Fees')
            cp = mcard
            comment = 'Mastercard Fees'
        else:
            credit = accountifie.gl.models.Account.objects.get(id=accountifie.environment.api.variable({'name': 'GL_ACCOUNTS_PAYABLE'}))
            cp = self.counterparty
            comment= "MasterCard ending #%s trans #%s: %s" % (self.card_number, self.id, cp)

        trans = []
        trans.append(dict(
            company=self.company,
            date=self.trans_date,
            trans_id='%s.%s.%s' % (self.short_code, self.id, 'CHRG'),
            bmo_id=self.id,
            comment= comment,
            long_desc= self.description,
            lines=[ # not sure of signs here
                (debit, float(self.amount), mcard, []),
                (credit, 0 - float(self.amount), cp, []),
                ]
            ))

        return trans


class AMEX(models.Model, BusinessModelObject):
    # note that this is only for charges, not for payments
    company = models.ForeignKey('gl.Company', default=accountifie._utils.get_default_company)

    date = models.DateField()
    amount = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    #These fields are added by our system or by a human
    counterparty = models.ForeignKey('gl.Counterparty', null=True, blank=True, help_text="We need to match this up")

    history = HistoricalRecords()
    short_code = 'AMEX'

    def __unicode__(self):
        return 'AMEX %s: %s: %s' % (self.id, self.date.isoformat(), self.counterparty)

    class Meta:
        app_label = 'base'
        verbose_name = "AMEX Transaction"
        verbose_name_plural = "AMEX Transactions"
        db_table = 'base_amex'

    def save(self):
        models.Model.save(self)
        self.update_gl()

    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    def get_gl_transactions(self):
        debit = accountifie.gl.models.Account.objects.get(display_name='Amex')
        credit = accountifie.gl.models.Account.objects.get(id=accountifie.environment.api.variable({'name': 'GL_ACCOUNTS_PAYABLE'}))
        amex = accountifie.gl.models.Counterparty.objects.get(id='amex')

        trans = []
        trans.append(dict(
            company=self.company,
            date=self.date,
            trans_id='%s.%s.%s' % (self.short_code, self.id, 'CHRG'),
            bmo_id=self.id,
            comment= "Paid AMEX. %s: %s" % (self.id, self.counterparty),
            lines=[ # not sure of signs here
                (debit, 0 - float(self.amount), amex),
                (credit, float(self.amount), self.counterparty),
                ]
            ))

        return trans

