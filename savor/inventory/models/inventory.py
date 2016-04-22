from django.db import models


class ProductLine(models.Model):
    description = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_productline'


class InventoryItem(models.Model):
    description = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)
    master_sku = models.CharField(max_length=20, blank=True, null=True)
    product_line = models.ForeignKey('inventory.ProductLine')

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_inventoryitem'


class SKU(models.Model):
    description = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_sku'


class SKUUnit(models.Model):
    quantity = models.PositiveIntegerField(default=0)
    inventory_item = models.ForeignKey(InventoryItem, blank=True, null=True)
    sku = models.ForeignKey(SKU, blank=True, null=True)
    rev_percent = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return '%d: %s' % (self.quantity, self.inventory_item)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_skuunit'
