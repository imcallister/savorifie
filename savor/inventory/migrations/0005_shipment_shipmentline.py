# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_skuunit_rev_percent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arrival_date', models.DateField()),
                ('description', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_shipment',
            },
        ),
        migrations.CreateModel(
            name='ShipmentLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True)),
                ('shipment', models.ForeignKey(to='inventory.Shipment')),
            ],
            options={
                'db_table': 'inventory_shipmentline',
            },
        ),
    ]
