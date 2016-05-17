import operator

from django.db import models

import accountifie.gl.bmo
import accountifie.common.models


class Warehouse(accountifie.common.models.McModel):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_warehouse'


class Shipper(accountifie.common.models.McModel):
    company = models.ForeignKey('gl.Counterparty')

    def __unicode__(self):
        return str(self.company)


class ShippingType(accountifie.common.models.McModel):
    shipper = models.ForeignKey(Shipper)
    label = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shippingtype'


class Shipment(accountifie.common.models.McModel, accountifie.gl.bmo.BusinessModelObject):
    arrival_date = models.DateField()
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)
    destination = models.ForeignKey('inventory.Warehouse', blank=True, null=True)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipment'


class ShipmentLine(accountifie.common.models.McModel):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipment = models.ForeignKey(Shipment)

    def __unicode__(self):
        return '%s:%s' % (self.shipment, self.id)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipmentline'


PACKING_TYPES = (
    ('box', 'box'),
    ('pouch', 'pouch'),
)

class ChannelShipmentType(accountifie.common.models.McModel):
    label = models.CharField(max_length=30)
    channel = models.ForeignKey('base.Channel')
    ship_type = models.ForeignKey(ShippingType)
    bill_to = models.CharField(max_length=100)
    use_pdf = models.BooleanField(default=False)
    packing_type = models.CharField(max_length=30, choices=PACKING_TYPES, default='box')

    def __unicode__(self):
        return self.label


FULFILL_CHOICES = (
    ('requested', 'requested'),
    ('partial', 'partial'),
    ('completed', 'completed'),
)


class Fulfillment(accountifie.common.models.McModel):
    request_date = models.DateField()
    warehouse = models.ForeignKey('inventory.Warehouse')
    order = models.ForeignKey('base.Sale')
    ship_type = models.ForeignKey(ShippingType, blank=True, null=True)
    bill_to = models.CharField(max_length=100, blank=True, null=True)
    use_pdf = models.BooleanField(default=False)
    packing_type = models.CharField(max_length=30, choices=PACKING_TYPES, default='box')

    properties = ['updates', 'fulfilllines', 'ship_info']

    def __unicode__(self):
        return '%s:%s' % (str(self.order), self.order.shipping_name)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillment'

    @property
    def ship_info(self):
        if self.ship_type and self.bill_to:
            return 'complete'
        else:
            return 'incomplete'

    @property
    def updates(self):
        return [u.to_json() for u in self.fulfillupdate_set.all()]

    @property
    def fulfilllines(self):
        return [u.to_json() for u in self.fulfillline_set.all()]

    @property
    def latest_status(self):
        updates = dict((u.update_date, u.status) for u in self.fulfillupdate_set.all())
        if len(updates) == 0:
            return 'requested'
        else:
            return max(updates.iteritems(), key=operator.itemgetter(0))[1]


class FulfillUpdate(accountifie.common.models.McModel):
    update_date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=FULFILL_CHOICES)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    fulfillment = models.ForeignKey(Fulfillment)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillupdate'


class FulfillLine(accountifie.common.models.McModel):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    fulfillment = models.ForeignKey(Fulfillment)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillline'


class InventoryTransfer(accountifie.common.models.McModel):
    transfer_date = models.DateField()
    location = models.ForeignKey('inventory.Warehouse', related_name='location')
    destination = models.ForeignKey('inventory.Warehouse', related_name='destination')


class TransferLine(accountifie.common.models.McModel):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    transfer = models.ForeignKey(InventoryTransfer)

    def __unicode__(self):
        return '%d %s' % (self.quantity, self.inventory_item.label)


class BatchRequest(accountifie.common.models.McModel):
    created_date = models.DateField()
    location = models.ForeignKey('inventory.Warehouse')
    fulfillments = models.ManyToManyField(Fulfillment, blank=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_batchrequest'

    @property
    def fulfillment_count(self):
        return self.fulfillments.all().count()


class TransferUpdate(accountifie.common.models.McModel):
    update_date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=FULFILL_CHOICES)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    transfer = models.ForeignKey(InventoryTransfer)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_transferupdate'


class WarehouseFulfill(accountifie.common.models.McModel):
    savor_order = models.ForeignKey('base.sale', blank=True, null=True)
    savor_transfer = models.ForeignKey('inventory.InventoryTransfer', blank=True, null=True)
    warehouse = models.ForeignKey('inventory.warehouse')
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

    ship_email = models.EmailField(max_length=254, blank=True, null=True)
    shipping_type = models.ForeignKey('inventory.ShippingType', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return 'Fill %s' % self.warehouse_pack_id


class WarehouseFulfillLine(accountifie.common.models.McModel):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    warehouse_fulfill = models.ForeignKey(WarehouseFulfill)

    def __unicode__(self):
        return '%s: %d %s' % (str(self.warehouse_fulfill), self.quantity, str(self.inventory_item))

