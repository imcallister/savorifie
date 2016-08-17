"""Models related to creating requests for fulfillment."""

import operator
import logging

from django.db import models

import accountifie.gl.bmo
import accountifie.gl.models
import accountifie.common.models

logger = logging.getLogger('default')


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


class Fulfillment(models.Model):
    request_date = models.DateField()
    warehouse = models.ForeignKey('inventory.Warehouse', blank=True, null=True)
    order = models.ForeignKey('base.Sale', related_name='fulfillments')
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
        app_label = 'inventory'
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
    fulfillment = models.ForeignKey('inventory.Fulfillment', related_name='fulfill_updates')

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillupdate'


class FulfillLine(models.Model):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    fulfillment = models.ForeignKey('inventory.Fulfillment', related_name='fulfill_lines')

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillline'
