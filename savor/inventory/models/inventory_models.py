from django.db import models

import accountifie.common.models

class ProductLine(accountifie.common.models.McModel):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_productline'


class InventoryItem(accountifie.common.models.McModel):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)
    master_sku = models.CharField(max_length=20, blank=True, null=True)
    product_line = models.ForeignKey('inventory.ProductLine')

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_inventoryitem'


class Product(accountifie.common.models.McModel):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_product'


class SKUUnit(accountifie.common.models.McModel):
    quantity = models.PositiveIntegerField(default=0)
    inventory_item = models.ForeignKey(InventoryItem, blank=True, null=True)
    sku = models.ForeignKey(Product, blank=True, null=True, related_name='skuunit')
    rev_percent = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return '%d: %s' % (self.quantity, self.inventory_item)

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_skuunit'
