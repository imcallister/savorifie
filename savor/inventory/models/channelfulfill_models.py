from django.db import models

import accountifie.common.models

PACKING_TYPES = (
    ('box', 'box'),
    ('pouch', 'pouch'),
)


class ChannelShipmentType(models.Model):
    label = models.CharField(max_length=30)
    channel = models.ForeignKey('sales.Channel')
    ship_type = models.ForeignKey('inventory.ShippingType')
    bill_to = models.CharField(max_length=100)
    use_pdf = models.BooleanField(default=False)
    packing_type = models.CharField(max_length=30, choices=PACKING_TYPES, default='box')
    ship_from = models.ForeignKey(accountifie.common.models.Address, blank=True, null=True)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_channelshipmenttype'
