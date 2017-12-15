# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-25 23:04
from __future__ import unicode_literals

import accountifie.gl.bmo
import accountifie.toolkit.utils.gl_helpers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('common', '0003_address_label'),
        ('gl', '0002_transaction_bmo_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateField()),
            ],
            options={
                'db_table': 'inventory_inventorytransfer',
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_date', models.DateField()),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_shipment',
            },
        ),
        migrations.CreateModel(
            name='ShipmentLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('company', models.ForeignKey(default='SAV', on_delete=django.db.models.deletion.CASCADE, to='gl.Company')),
                ('inventory_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.InventoryItem')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Shipment')),
            ],
            options={
                'db_table': 'inventory_shipmentline',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='ShipOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=30)),
                ('bill_to', models.CharField(max_length=100)),
                ('use_pdf', models.BooleanField(default=False)),
                ('packing_type', models.CharField(choices=[(b'box', b'box'), (b'pouch', b'pouch')], default=b'box', max_length=30)),
                ('ship_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address')),
            ],
            options={
                'db_table': 'inventory_channelshipmenttype',
            },
        ),
        migrations.CreateModel(
            name='Shipper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gl.Counterparty')),
            ],
            options={
                'db_table': 'inventory_shipper',
            },
        ),
        migrations.CreateModel(
            name='ShippingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
                ('shipper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Shipper')),
            ],
            options={
                'db_table': 'inventory_shippingtype',
            },
        ),
        migrations.CreateModel(
            name='TransferLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.InventoryItem')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryTransfer')),
            ],
            options={
                'db_table': 'inventory_transferline',
            },
        ),
        migrations.CreateModel(
            name='TransferUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_date', models.DateField()),
                ('comment', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')], max_length=30)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('shipper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Shipper')),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryTransfer')),
            ],
            options={
                'db_table': 'inventory_transferupdate',
            },
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_warehouse',
            },
        ),
        migrations.AddField(
            model_name='shipoption',
            name='ship_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ShippingType'),
        ),
        migrations.AddField(
            model_name='shipment',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='shipment',
            name='sent_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gl.Counterparty'),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='inventorytransfer',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location', to='inventory.Warehouse'),
        ),
    ]
