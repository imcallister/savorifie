# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20160422_1554'),
        ('inventory', '0020_auto_20160427_1557'),
    ]

    operations = [
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
                ('ship_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('shipping_code', models.CharField(max_length=100, null=True, blank=True)),
                ('tracking_number', models.CharField(max_length=100, null=True, blank=True)),
                ('savor_order', models.ForeignKey(blank=True, to='base.Sale', null=True)),
                ('savor_transfer', models.ForeignKey(blank=True, to='inventory.InventoryTransfer', null=True)),
                ('warehouse', models.ForeignKey(to='inventory.Warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseFulfillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True)),
                ('warehouse_fulfill', models.ForeignKey(to='inventory.WarehouseFulfill')),
            ],
        ),
    ]
