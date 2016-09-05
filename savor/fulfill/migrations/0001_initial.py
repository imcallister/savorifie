# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0042_auto_20160904_0000'),
        ('sales', '0001_initial'),
        ('common', '0003_address_label'),
        ('products', '0001_initial'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='BatchRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateField()),
                ('comment', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'inventory_batchrequest',
            },
        ),
        migrations.CreateModel(
            name='FulfillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'inventory_fulfillline',
            },
        ),
        migrations.CreateModel(
            name='Fulfillment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_date', models.DateField()),
                ('bill_to', models.CharField(max_length=100, null=True, blank=True)),
                ('use_pdf', models.BooleanField(default=False)),
                ('packing_type', models.CharField(default=b'box', max_length=30, choices=[(b'box', b'box'), (b'pouch', b'pouch')])),
                ('status', models.CharField(max_length=20, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')])),
                ('order', models.ForeignKey(related_name='fulfillments', to='sales.Sale')),
                ('ship_from', models.ForeignKey(blank=True, to='common.Address', null=True)),
                ('ship_type', models.ForeignKey(blank=True, to='inventory.ShippingType', null=True)),
                ('warehouse', models.ForeignKey(blank=True, to='inventory.Warehouse', null=True)),
            ],
            options={
                'db_table': 'inventory_fulfillment',
            },
        ),
        migrations.CreateModel(
            name='FulfillUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_date', models.DateField()),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
                ('status', models.CharField(max_length=30, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')])),
                ('tracking_number', models.CharField(max_length=100, null=True, blank=True)),
                ('fulfillment', models.ForeignKey(related_name='fulfill_updates', to='fulfill.Fulfillment')),
                ('shipper', models.ForeignKey(blank=True, to='inventory.Shipper', null=True)),
            ],
            options={
                'db_table': 'inventory_fulfillupdate',
            },
        ),
        migrations.CreateModel(
            name='WarehouseFulfill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('warehouse_pack_id', models.CharField(max_length=100, null=True, blank=True)),
                ('order_date', models.DateField(null=True, blank=True)),
                ('request_date', models.DateField(null=True, blank=True)),
                ('ship_date', models.DateField(null=True, blank=True)),
                ('shipping_name', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_attn', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address1', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address2', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address3', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_city', models.CharField(max_length=50, null=True, blank=True)),
                ('shipping_zip', models.CharField(max_length=20, null=True, blank=True)),
                ('shipping_province', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_country', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_phone', models.CharField(max_length=30, null=True, blank=True)),
                ('weight', models.DecimalField(null=True, max_digits=12, decimal_places=6, blank=True)),
                ('shipping_cost', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('handling_cost', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('ship_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('tracking_number', models.CharField(max_length=100, null=True, blank=True)),
                ('fulfillment', models.ForeignKey(blank=True, to='fulfill.Fulfillment', null=True)),
                ('savor_order', models.ForeignKey(blank=True, to='sales.Sale', null=True)),
                ('savor_transfer', models.ForeignKey(blank=True, to='inventory.InventoryTransfer', null=True)),
                ('shipping_type', models.ForeignKey(blank=True, to='inventory.ShippingType', null=True)),
                ('warehouse', models.ForeignKey(to='inventory.Warehouse')),
            ],
            options={
                'db_table': 'inventory_warehousefulfill',
            },
        ),
        migrations.CreateModel(
            name='WarehouseFulfillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, to='products.InventoryItem', null=True)),
                ('warehouse_fulfill', models.ForeignKey(related_name='fulfill_lines', to='fulfill.WarehouseFulfill')),
            ],
            options={
                'db_table': 'inventory_warehousefulfillline',
            },
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='fulfillment',
            field=models.ForeignKey(related_name='fulfill_lines', to='fulfill.Fulfillment'),
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='inventory_item',
            field=models.ForeignKey(blank=True, to='products.InventoryItem', null=True),
        ),
        migrations.AddField(
            model_name='batchrequest',
            name='fulfillments',
            field=models.ManyToManyField(to='fulfill.Fulfillment', blank=True),
        ),
        migrations.AddField(
            model_name='batchrequest',
            name='location',
            field=models.ForeignKey(to='inventory.Warehouse'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
