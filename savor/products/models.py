from django.db import models


class ProductLine(models.Model):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'products'
        db_table = 'inventory_productline'


class InventoryItem(models.Model):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)
    master_sku = models.CharField(max_length=20, blank=True, null=True)
    product_line = models.ForeignKey(ProductLine)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'products'
        db_table = 'inventory_inventoryitem'


class Product(models.Model):
    description = models.CharField(max_length=200)
    label = models.CharField(max_length=20)

    def __unicode__(self):
        return self.label

    class Meta:
        app_label = 'products'
        db_table = 'inventory_product'


class SKUUnit(models.Model):
    quantity = models.PositiveIntegerField(default=0)
    inventory_item = models.ForeignKey(InventoryItem, blank=True, null=True)
    sku = models.ForeignKey(Product, blank=True, null=True, related_name='skuunit')
    rev_percent = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return '%d: %s' % (self.quantity, self.inventory_item)

    class Meta:
        app_label = 'products'
        db_table = 'inventory_skuunit'
