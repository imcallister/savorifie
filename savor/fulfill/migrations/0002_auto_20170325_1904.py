# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-25 23:04
from __future__ import unicode_literals

import accountifie.toolkit.utils.gl_helpers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0003_address_label'),
        ('gl', '0002_transaction_bmo_id'),
        ('fulfill', '0001_initial'),
        ('products', '0001_initial'),
        ('inventory', '0001_initial'),
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousefulfill',
            name='savor_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.Sale'),
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='savor_transfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryTransfer'),
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='shipping_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.ShippingType'),
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='shippingcharge',
            name='company',
            field=models.ForeignKey(default='SAV', on_delete=django.db.models.deletion.CASCADE, to='gl.Company'),
        ),
        migrations.AddField(
            model_name='shippingcharge',
            name='fulfillment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fulfill.Fulfillment'),
        ),
        migrations.AddField(
            model_name='shippingcharge',
            name='shipper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Shipper'),
        ),
        migrations.AddField(
            model_name='fulfillupdate',
            name='fulfillment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfill_updates', to='fulfill.Fulfillment'),
        ),
        migrations.AddField(
            model_name='fulfillupdate',
            name='shipper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Shipper'),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfillments', to='sales.Sale'),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='ship_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address'),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='ship_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.ShippingType'),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='fulfillment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfill_lines', to='fulfill.Fulfillment'),
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='inventory_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.InventoryItem'),
        ),
        migrations.AddField(
            model_name='batchrequest',
            name='fulfillments',
            field=models.ManyToManyField(blank=True, to='fulfill.Fulfillment'),
        ),
        migrations.AddField(
            model_name='batchrequest',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Warehouse'),
        ),
    ]
