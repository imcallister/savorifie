from django.db import models

import accountifie.common.models


class FIFOAssignment(accountifie.common.models.McModel):
    shipment_line = models.ForeignKey('inventory.ShipmentLine')
    unit_sale = models.ForeignKey('base.UnitSale', blank=True)
    quantity = models.PositiveIntegerField()

    def __unicode__(self):
        return '%s --> %s' % (str(self.unit_sale), str(self.shipment_line),)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fifoassignment'