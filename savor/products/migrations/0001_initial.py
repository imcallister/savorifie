# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-25 23:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
                ('master_sku', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'products_inventoryitem',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'products_product',
            },
        ),
        migrations.CreateModel(
            name='ProductLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('label', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'products_productline',
            },
        ),
        migrations.CreateModel(
            name='SKUUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('rev_percent', models.PositiveIntegerField(default=0)),
                ('inventory_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.InventoryItem')),
                ('sku', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skuunit', to='products.Product')),
            ],
            options={
                'db_table': 'products_skuunit',
            },
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='product_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.ProductLine'),
        ),
    ]
