import logging

from django.db import models


logger = logging.getLogger('default')



class COGSAssignment(models.Model):
    shipment_line = models.ForeignKey('inventory.ShipmentLine')
    unit_sale = models.ForeignKey('sales.UnitSale', blank=True)
    quantity = models.IntegerField()

    def __unicode__(self):
        return '%s --> %s' % (str(self.unit_sale), str(self.shipment_line),)

    class Meta:
        app_label = 'accounting'
        db_table = 'accounting_cogsassignment'