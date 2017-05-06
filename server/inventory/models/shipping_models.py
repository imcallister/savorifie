from decimal import Decimal

from django.db import models

import accountifie.gl.models
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func


class Shipper(models.Model):
    company = models.ForeignKey('gl.Counterparty')

    def __unicode__(self):
        return str(self.company)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipper'


class ShippingType(models.Model):
    shipper = models.ForeignKey('inventory.Shipper')
    label = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shippingtype'


class Shipment(models.Model):
    arrival_date = models.DateField()
    sent_by = models.ForeignKey('gl.Counterparty')
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)
    destination = models.ForeignKey('inventory.Warehouse', blank=True, null=True)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipment'


class ShipmentLine(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)
    inventory_item = models.ForeignKey('products.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipment = models.ForeignKey('inventory.Shipment')

    short_code = 'SHPLN'

    def __unicode__(self):
        return '%s:%s' % (self.shipment, self.inventory_item)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipmentline'

    def get_gl_transactions(self):
        """
        Make transfers to inventory accounts.

        Inventory costs are booked to the 'omnibus'.
        inventory account. This function books transfers
        to the inventory accounts specific to each SKU.
        """
        product_line = self.inventory_item.product_line.label
        inv_item = self.inventory_item.label
        inv_acct_path = 'assets.curr.inventory.%s.%s' % (product_line, inv_item)
        inv_acct = accountifie.gl.models.Account.objects.filter(path=inv_acct_path).first().id

        GEN_INVENTORY = api_func('environment', 'variable', 'GL_INVENTORY')
        gen_inv_acct = GEN_INVENTORY

        counterparty = self.shipment.sent_by.id
        amount = Decimal(self.cost) * Decimal(self.quantity)

        tran = []
        tran = dict(company=self.company,
                    date=self.shipment.arrival_date,
                    comment="%s" % str(self),
                    trans_id='%s.%s.LINE' % (self.short_code, self.id),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    lines=[(inv_acct, amount, counterparty, []),
                           (gen_inv_acct, -amount, counterparty, [])]
                    )
        return [tran]
