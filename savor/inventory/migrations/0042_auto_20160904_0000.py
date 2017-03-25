# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_auto_20160904_0000'),
        ('inventory', '0041_auto_20160827_1500'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='batchrequest',
            name='fulfillments',
        ),
        migrations.RemoveField(
            model_name='batchrequest',
            name='location',
        ),
        migrations.RemoveField(
            model_name='fulfillline',
            name='fulfillment',
        ),
        migrations.RemoveField(
            model_name='fulfillline',
            name='inventory_item',
        ),
        migrations.RemoveField(
            model_name='fulfillment',
            name='order',
        ),
        migrations.RemoveField(
            model_name='fulfillment',
            name='ship_from',
        ),
        migrations.RemoveField(
            model_name='fulfillment',
            name='ship_type',
        ),
        migrations.RemoveField(
            model_name='fulfillment',
            name='warehouse',
        ),
        migrations.RemoveField(
            model_name='fulfillupdate',
            name='fulfillment',
        ),
        migrations.RemoveField(
            model_name='fulfillupdate',
            name='shipper',
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='product_line',
        ),
        migrations.RemoveField(
            model_name='skuunit',
            name='inventory_item',
        ),
        migrations.RemoveField(
            model_name='skuunit',
            name='sku',
        ),
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='fulfillment',
        ),
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='savor_order',
        ),
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='savor_transfer',
        ),
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='shipping_type',
        ),
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='warehouse',
        ),
        migrations.RemoveField(
            model_name='warehousefulfillline',
            name='inventory_item',
        ),
        migrations.RemoveField(
            model_name='warehousefulfillline',
            name='warehouse_fulfill',
        ),
        migrations.AlterField(
            model_name='channelshipmenttype',
            name='channel',
            field=models.ForeignKey(to='sales.Channel'),
        ),
        migrations.AlterField(
            model_name='shipmentline',
            name='inventory_item',
            field=models.ForeignKey(blank=True, to='products.InventoryItem', null=True),
        ),
        migrations.AlterField(
            model_name='transferline',
            name='inventory_item',
            field=models.ForeignKey(blank=True, to='products.InventoryItem', null=True),
        ),
        migrations.DeleteModel(
            name='BatchRequest',
        ),
        migrations.DeleteModel(
            name='FulfillLine',
        ),
        migrations.DeleteModel(
            name='Fulfillment',
        ),
        migrations.DeleteModel(
            name='FulfillUpdate',
        ),
        migrations.DeleteModel(
            name='InventoryItem',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.DeleteModel(
            name='ProductLine',
        ),
        migrations.DeleteModel(
            name='SKUUnit',
        ),
        migrations.DeleteModel(
            name='WarehouseFulfill',
        ),
        migrations.DeleteModel(
            name='WarehouseFulfillLine',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
