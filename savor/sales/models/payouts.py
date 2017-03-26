from decimal import Decimal
import logging

from django.db import models


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
        return '%s:%s' % (self.payout, self.id)


class Payout(models.Model):
    channel = models.ForeignKey('sales.Channel')
    payout_date = models.DateField()
    payout = models.DecimalField(max_digits=8, decimal_places=2)
    paid_thru = models.ForeignKey('gl.Counterparty', blank=True, null=True,
                                  related_name='ch_payout_paid_thru',
                                  limit_choices_to={'id__in': ['SHOPIFY', 'PAYPAL', 'AMZN', 'AMZN_PMTS']})

    class Meta:
        app_label = 'sales'
        db_table = 'sales_payout'

    def __unicode__(self):
        return '%s:%s:%s' % (self.channel, self.paid_thru, self.id)

    def calcd_payout(self):
        return sum([s.amount for s in self.payout_line.all()])

