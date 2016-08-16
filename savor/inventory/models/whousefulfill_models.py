from django.db import models


class WarehouseFulfill(models.Model):
    fulfillment = models.ForeignKey('inventory.fulfillment', blank=True, null=True)
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

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_warehousefulfill'


class WarehouseFulfillLine(models.Model):
    inventory_item = models.ForeignKey('inventory.InventoryItem',
                                       blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    warehouse_fulfill = models.ForeignKey(WarehouseFulfill,
                                          related_name='fulfill_lines')

    def __unicode__(self):
        return '%s: %d %s' % (str(self.warehouse_fulfill),
                              self.quantity,
                              str(self.inventory_item))

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_warehousefulfillline'
