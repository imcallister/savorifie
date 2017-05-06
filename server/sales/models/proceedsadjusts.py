from decimal import Decimal
import logging

from django.db import models


DZERO = Decimal('0')

logger = logging.getLogger('default')


TYPE_TAGS = (
    ('CHANNEL_FEES', 'Channel Fees'),
    ('GIFTWRAP_FEES', 'Giftwrap'),
    ('DISCOUNT', 'Discount'),
    ('SHIPPING_CHARGE', 'Shipping Charge'),
    ('GIFTCARD_REDEMPTION', 'Giftcard redemption'),
    ('PAYMENT', 'Standalone Payment'),
    )


class ProceedsAdjustment(models.Model):
    sale = models.ForeignKey('sales.Sale', related_name='proceedsadjustment_sale', null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    adjust_type = models.CharField(max_length=20, choices=TYPE_TAGS, blank=True, null=True)

    class Meta:
        app_label = 'sales'
        db_table = 'sales_proceedsadjustment'

    def __unicode__(self):
        return str(self.id)
