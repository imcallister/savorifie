"""Models related to creating requests for fulfillment."""

import operator
import logging
from decimal import Decimal

from django.db import models

from accountifie.gl.bmo import BusinessModelObject
import accountifie.gl.models
import accountifie.common.models
from accountifie.toolkit.utils import get_default_company


logger = logging.getLogger('default')

DZERO = Decimal('0')

FULFILL_CHOICES = (
    ('back-ordered', 'back-ordered'),
    ('requested', 'requested'),
    ('partial', 'partial'),
    ('mismatched', 'mismatched'),
    ('completed', 'completed'),
)

PACKING_TYPES = (
    ('box', 'box'),
    ('pouch', 'pouch'),
)


class ShippingCharge(models.Model, BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    account = models.CharField(max_length=25, blank=True, null=True)
    external_id = models.CharField(max_length=50, blank=True, null=True)
    packing_id = models.CharField(max_length=50, blank=True, null=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_number = models.CharField(max_length=25, blank=True, null=True)
    ship_date = models.DateField()
    charge = models.DecimalField(max_digits=8, decimal_places=2)
    fulfillment = models.ForeignKey('fulfill.Fulfillment', blank=True, null=True)
    order_related = models.BooleanField(default=True)
    comment = models.TextField(null=True, blank=True)

    short_code = 'SHP'

    def save(self, update_gl=True):
        models.Model.save(self)
        if update_gl:
            self.update_gl()
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    def get_gl_transactions(self):
        comment = '%s. Fulfill %s. %s' % (self.id,
                                          str(self.fulfillment),
                                          str(self.shipper))
        
        if self.comment:
            comment += '. %s' % self.comment
        tran = dict(
                    company=self.company,
                    date=self.ship_date,
                    date_end=None,
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'CHG'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    comment=comment
                )

        cp = self.shipper.company
        
        # HARD CODE
        ap_acct = '3006'
        exp_acct = '5070'

        lines = [(ap_acct, DZERO - Decimal(self.charge), cp, []),
               (exp_acct, Decimal(self.charge), cp, [])]

        tran['lines'] = lines
        return [tran]




class Fulfillment(models.Model):
    request_date = models.DateField()
    warehouse = models.ForeignKey('inventory.Warehouse', blank=True, null=True)
    order = models.ForeignKey('sales.Sale', related_name='fulfillments')
    ship_type = models.ForeignKey('inventory.ShippingType', blank=True, null=True)
    bill_to = models.CharField(max_length=100, blank=True, null=True)
    use_pdf = models.BooleanField(default=False)
    packing_type = models.CharField(max_length=30, choices=PACKING_TYPES, default='box')
    ship_from = models.ForeignKey(accountifie.common.models.Address, blank=True, null=True)
    status = models.CharField(max_length=20, choices=FULFILL_CHOICES)
    properties = ['updates', 'ship_info', 'latest_status']

    def __unicode__(self):
        return '%s:%s %s' % (self.id, str(self.order), self.order.shipping_name)

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_fulfillment'

    @property
    def ship_info(self):
        if self.ship_type and self.bill_to:
            return 'complete'
        elif self.ship_type and self.ship_type.label=='BY_HAND':
            return 'complete'
        else:
            return 'incomplete'

    @property
    def items_string(self):
        items = [(l.quantity, l.inventory_item.label) for l in self.fulfill_lines.all()]
        items = sorted(items, key=lambda x: x[1])
        return ','.join(['%s %s' % (i[0], i[1]) for i in items])

    @property
    def latest_status(self):
        updates = dict((u.update_date, u.status) for u in self.fulfillupdate_set.all())
        if len(updates) == 0:
            return 'requested'
        else:
            return max(updates.iteritems(), key=operator.itemgetter(0))[1]


class FulfillUpdate(models.Model):
    update_date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=FULFILL_CHOICES)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    fulfillment = models.ForeignKey(Fulfillment, related_name='fulfill_updates')

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_fulfillupdate'


class FulfillLine(models.Model):
    inventory_item = models.ForeignKey('products.InventoryItem', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    fulfillment = models.ForeignKey(Fulfillment, related_name='fulfill_lines')

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_fulfillline'


class WarehouseFulfill(models.Model):
    fulfillment = models.ForeignKey(Fulfillment, blank=True, null=True, related_name='warehousefulfill')
    savor_order = models.ForeignKey('sales.Sale', blank=True, null=True)
    savor_transfer = models.ForeignKey('inventory.InventoryTransfer', blank=True, null=True)
    warehouse = models.ForeignKey('inventory.Warehouse')
    warehouse_pack_id = models.CharField(max_length=100, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    request_date = models.DateField(blank=True, null=True)
    ship_date = models.DateField(blank=True, null=True)
    shipping_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_attn = models.CharField(max_length=100, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=100, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=100, blank=True, null=True)
    shipping_address3 = models.CharField(max_length=100, blank=True, null=True)
    shipping_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_zip = models.CharField(max_length=20, blank=True, null=True)
    shipping_province = models.CharField(max_length=30, blank=True, null=True)
    shipping_country = models.CharField(max_length=30, blank=True, null=True)
    shipping_phone = models.CharField(max_length=30, blank=True, null=True)

    weight = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    handling_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    ship_email = models.EmailField(max_length=254, blank=True, null=True)
    shipping_type = models.ForeignKey('inventory.ShippingType', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return 'Fill %s' % self.warehouse_pack_id

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_warehousefulfill'


class WarehouseFulfillLine(models.Model):
    inventory_item = models.ForeignKey('products.InventoryItem',
                                       blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    warehouse_fulfill = models.ForeignKey(WarehouseFulfill,
                                          related_name='fulfill_lines')

    def __unicode__(self):
        return '%s: %d %s' % (str(self.warehouse_fulfill),
                              self.quantity,
                              str(self.inventory_item))

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_warehousefulfillline'


class BatchRequest(models.Model):
    created_date = models.DateField()
    location = models.ForeignKey('inventory.Warehouse')
    fulfillments = models.ManyToManyField('fulfill.Fulfillment', blank=True)
    comment = models.TextField(blank=True, null=True)

    properties = ['fulfillment_count',]

    class Meta:
        app_label = 'fulfill'
        db_table = 'inventory_batchrequest'

    @property
    def fulfillment_count(self):
        return self.fulfillments.all().count()
