# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    state_operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
                ('master_sku', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'db_table': 'inventory_inventoryitem',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_product',
            },
        ),
        migrations.CreateModel(
            name='ProductLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_productline',
            },
        ),
        migrations.CreateModel(
            name='SKUUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('rev_percent', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, to='products.InventoryItem', null=True)),
                ('sku', models.ForeignKey(related_name='skuunit', blank=True, to='products.Product', null=True)),
            ],
            options={
                'db_table': 'inventory_skuunit',
            },
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='product_line',
            field=models.ForeignKey(to='products.ProductLine'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
