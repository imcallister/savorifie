
from django.db import models


class Warehouse(models.Model):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_warehouse'


class InventoryTransfer(models.Model):
    transfer_date = models.DateField()
    location = models.ForeignKey('inventory.Warehouse', related_name='location')
    destination = models.ForeignKey('inventory.Warehouse', related_name='destination')

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_inventorytransfer'

    def __unicode__(self):
        return '%s to %s. %s' % (self.location.label, self.destination.label, self.transfer_date.strftime('%d-%b-%y'))



class TransferLine(models.Model):
    inventory_item = models.ForeignKey('products.InventoryItem', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    transfer = models.ForeignKey('inventory.InventoryTransfer')

    def __unicode__(self):
        return '%d %s' % (self.quantity, self.inventory_item.label)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_transferline'




FULFILL_CHOICES = (
    ('back-ordered', 'back-ordered'),
    ('requested', 'requested'),
    ('partial', 'partial'),
    ('mismatched', 'mismatched'),
    ('completed', 'completed'),
)


class TransferUpdate(models.Model):
    update_date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, choices=FULFILL_CHOICES)
    shipper = models.ForeignKey('inventory.Shipper', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    transfer = models.ForeignKey('inventory.InventoryTransfer')

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_transferupdate'
