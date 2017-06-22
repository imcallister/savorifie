from decimal import Decimal
import logging

from django.db import models

import accountifie.gl.bmo
import sales_funcs
from accountifie.toolkit.utils import get_default_company

DZERO = Decimal('0')

logger = logging.getLogger('default')


class Channel(models.Model):
    label = models.CharField(max_length=20)
    counterparty = models.ForeignKey('gl.Counterparty')

    class Meta:
        app_label = 'sales'
        db_table = 'sales_channel'

    def __unicode__(self):
        return self.label

CHANNELS = [
    ['shopify', "Shopify"],
]


PAYOUT_TAGS = (
    ('STANDALONE', 'Standalone'),
    ('REFUND', 'Refund')
    )

class PayoutLine(models.Model):
    sale = models.ForeignKey('sales.Sale', related_name='payoutline_sale', null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    tag = models.CharField(max_length=20, choices=PAYOUT_TAGS, blank=True, null=True)
    payout = models.ForeignKey('sales.Payout', related_name='payout_line')

    class Meta:
        app_label = 'sales'
        db_table = 'sales_payoutline'

    def __unicode__(self):
        return '%s' % (self.id)


class Payout(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)
    channel = models.ForeignKey('sales.Channel')
    payout_date = models.DateField()
    payout = models.DecimalField(max_digits=8, decimal_places=2)
    paid_thru = models.ForeignKey('gl.Counterparty', blank=True, null=True,
                                  related_name='ch_payout_paid_thru',
                                  limit_choices_to={'id__in': ['SHOPIFY', 'PAYPAL', 'AMZN', 'AMZN_PMTS']})

    short_code = 'PAYOUT'

    class Meta:
        app_label = 'sales'
        db_table = 'sales_payout'

    def __unicode__(self):
        return '%s:%s:%s' % (self.channel, self.paid_thru, self.id)

    def save(self):
        models.Model.save(self)
        self.update_gl()

    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    def calcd_payout(self):
        return sum([s.amount for s in self.payout_line.all()])

    def get_gl_transactions(self):
        
        rec_acct = sales_funcs.get_receiveables_account(None, self.paid_thru.id)
        general_rec_acct = sales_funcs.get_receiveables_account(None, None)

        total = self.calcd_payout()
        
        tran = {}
        tran['company'] = get_default_company()
        tran['bmo_id'] = '%s.%s' % (self.short_code, self.id)
        tran['lines'] = []
        tran['date'] = self.payout_date
        tran['comment'] = "Payout - %s: %s" % (self.paid_thru, self.id)
        tran['trans_id'] = '%s.%s.%s' % (self.short_code, self.id, 'PAYOUT')
        tran['lines'] += [(rec_acct, -total, self.paid_thru.id, [])]
        tran['lines'] += [(general_rec_acct, total, self.paid_thru.id, [])]
        return [tran]


