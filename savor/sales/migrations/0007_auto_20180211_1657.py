# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-02-11 21:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_sale_checkout_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proceedsadjustment',
            name='adjust_type',
            field=models.CharField(blank=True, choices=[(b'CHANNEL_FEES', b'Channel Fees'), (b'GIFTWRAP_FEES', b'Giftwrap'), (b'DISCOUNT', b'Discount'), (b'SHIPPING_CHARGE', b'Shipping Charge'), (b'GIFTCARD_REDEMPTION', b'Giftcard redemption'), (b'PAYMENT', b'Standalone Payment')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='special_sale',
            field=models.CharField(blank=True, choices=[(b'press', b'Press Sample'), (b'consignment', b'Consignment'), (b'prize', b'Gift/Prize'), (b'retailer', b'Retailer Sample')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='unitsale',
            name='date',
            field=models.DateField(default=datetime.date(2018, 1, 1)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='unitsale',
            name='sku',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='products.Product'),
            preserve_default=False,
        ),
    ]
