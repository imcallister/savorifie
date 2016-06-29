import logging

from django.db import models

import accountifie.common.models
from accountifie.common.api import api_func

logger = logging.getLogger('default')


def fifo_assign(unit_sale_id, to_assign):
    ship_lines = api_func('inventory', 'shipmentline')
    avail_slines = {}
    for l in ship_lines:
        if l['inventory_item'] not in avail_slines:
            avail_slines[l['inventory_item']] = l['id']
        
    for sku in to_assign:
        fifo_info = {}
        fifo_info['shipment_line_id'] = avail_slines[sku]
        fifo_info['unit_sale_id'] = unit_sale_id
        fifo_info['quantity'] = to_assign[sku]
        COGSAssignment(**fifo_info).save()


class COGSAssignment(accountifie.common.models.McModel):
    shipment_line = models.ForeignKey('inventory.ShipmentLine')
    unit_sale = models.ForeignKey('base.UnitSale', blank=True)
    quantity = models.PositiveIntegerField()

    def __unicode__(self):
        return '%s --> %s' % (str(self.unit_sale), str(self.shipment_line),)

    class Meta:
        app_label = 'accounting'
        db_table = 'accounting_cogsassignment'