from django.db import models

import accountifie.gl.bmo

class Warehouse(models.Model):
    description = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_warehouse'


class Shipper(models.Model):
    company = models.ForeignKey('gl.Counterparty')

    def __unicode__(self):
        return str(self.company)

class ShippingType(models.Model):
    shipper = models.ForeignKey(Shipper)
    short_code = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s - %s'  % (self.shipper.company.id, self.short_code)

class Shipment(models.Model, accountifie.gl.bmo.BusinessModelObject):
    arrival_date = models.DateField()
    description = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)
    destination = models.ForeignKey('inventory.Warehouse', blank=True, null=True)

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipment'


class ShipmentLine(models.Model):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipment = models.ForeignKey(Shipment)

    def __unicode__(self):
        return '%s:%s' % (self.shipment, self.id)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_shipmentline'

class ChannelShipmentType(models.Model):
    short_code = models.CharField(max_length=30)
    channel = models.ForeignKey('base.Channel')
    ship_type = models.ForeignKey(ShippingType)
    bill_to = models.CharField(max_length=100)


FULFILL_CHOICES = (
    ('requested', 'requested'),
    ('partial', 'partial'),
    ('completed', 'completed'),
)


class Fulfillment(models.Model):
    request_date = models.DateField()
    warehouse = models.ForeignKey('inventory.Warehouse')
    order = models.ForeignKey('base.Sale')
    ship_type = models.ForeignKey(ShippingType, blank=True, null=True)
    bill_to = models.CharField(max_length=100, default='missing')

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillment'


class FulfillUpdate(models.Model):
    update_date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=FULFILL_CHOICES)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    fulfillment = models.ForeignKey(Fulfillment)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillupdate'


class FulfillLine(models.Model):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    fulfillment = models.ForeignKey(Fulfillment)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_fulfillline'




class InventoryTransfer(models.Model):
    transfer_date = models.DateField()
    location = models.ForeignKey('inventory.Warehouse', related_name='location')
    destination = models.ForeignKey('inventory.Warehouse', related_name='destination')


class TransferLine(models.Model):
    inventory_item = models.ForeignKey('inventory.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    transfer = models.ForeignKey(InventoryTransfer)

    def __unicode__(self):
        return '%d %s at %.2f' % (self.quantity, self.inventory_item.short_code, self.cost )
    




