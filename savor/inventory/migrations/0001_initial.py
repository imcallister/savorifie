# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_inventoryitem',
            },
        ),
        migrations.CreateModel(
            name='ProductLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'inventory_productline',
            },
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=20)),
                ('items', models.ManyToManyField(to='inventory.InventoryItem')),
            ],
            options={
                'db_table': 'inventory_sku',
            },
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='product_line',
            field=models.ForeignKey(to='inventory.ProductLine'),
        ),
    ]
