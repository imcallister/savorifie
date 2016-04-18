# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_shipmentline_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('cost', models.DecimalField(default=0, max_digits=6, decimal_places=2)),
                ('inventory_item', models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InventoryTransfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transfer_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='destination',
            field=models.ForeignKey(related_name='destination', to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='location',
            field=models.ForeignKey(related_name='location', to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='picking_list',
            field=models.ManyToManyField(to='inventory.InventoryLine', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='shipment',
            name='destination',
            field=models.ForeignKey(blank=True, to='inventory.Warehouse', null=True),
        ),
    ]
