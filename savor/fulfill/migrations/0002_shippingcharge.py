# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0044_auto_20160905_1000'),
        ('fulfill', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingCharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.CharField(max_length=25, null=True, blank=True)),
                ('tracking_number', models.CharField(max_length=50, null=True, blank=True)),
                ('invoice_number', models.CharField(max_length=25, null=True, blank=True)),
                ('ship_date', models.DateField()),
                ('charge', models.DecimalField(max_digits=8, decimal_places=2)),
                ('fulfillment', models.ForeignKey(blank=True, to='fulfill.Fulfillment', null=True)),
                ('shipper', models.ForeignKey(blank=True, to='inventory.Shipper', null=True)),
            ],
        ),
    ]
