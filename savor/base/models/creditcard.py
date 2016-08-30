from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.models
from accountifie.gl.bmo import BusinessModelObject
from accountifie.toolkit.utils import get_default_company
import accountifie.environment.apiv1 as env_api


class CreditCardTrans(models.Model, BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)
    card_company = models.ForeignKey('gl.Counterparty', related_name='card_company')
    counterparty = models.ForeignKey('gl.Counterparty',
                                     null=True,
                                     blank=True,
                                     related_name='counterparty')

    trans_date = models.DateField()
    post_date = models.DateField()
    trans_type = models.CharField(max_length=20, null=True)
    trans_id = models.CharField(max_length=50, null=True, unique=True)

    amount = models.FloatField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    payee = models.CharField(max_length=200, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    expense_comment = models.CharField(max_length=200, null=True, blank=True)
    expense_acct = models.ForeignKey('gl.Account', null=True, blank=True,
                                     help_text='Optional. For related expense created from Credit Card Trans')

    def __unicode__(self):
        return '%s:%s' % (str(self.card_company), self.trans_id)

    class Meta:
        app_label = 'base'
        verbose_name = "Credit Card Transaction"
        verbose_name_plural = "Credit Card Transactions"
        db_table = 'base_creditcardtransactions'

    history = HistoricalRecords()
    short_code = 'CCARD'

    def save(self):
        models.Model.save(self)
        self.update_gl()

    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    def get_gl_transactions(self):
        mcard = accountifie.gl.models.Counterparty.objects.get(id='MCARD')
        debit = accountifie.gl.models.Account.objects \
                                             .get(display_name='Mastercard')
        credit = accountifie.gl.models.Account.objects \
                                              .get(id=env_api.variable(GL_ACCOUNTS_PAYABLE, {}))
        cp = self.counterparty
        comment= "MasterCard ending #%s trans #%s: %s" % (self.card_number, self.id, cp)

        trans = []
        trans.append(dict(
            company=self.company,
            date=self.trans_date,
            trans_id='%s.%s.%s' % (self.short_code, self.id, 'CHRG'),
            bmo_id='%s.%s' % (self.short_code, self.id),
            comment= comment,
            long_desc= self.description,
            lines=[ # not sure of signs here
                (debit, float(self.amount), mcard, []),
                (credit, 0 - float(self.amount), cp, []),
                ]
            ))

        return trans


