# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0013_auto_20160422_1554'),
        ('inventory', '0012_auto_20160422_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelShipmentTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_code', models.CharField(max_length=30)),
                ('bill_to', models.CharField(max_length=100)),
                ('channel', models.ForeignKey(to='base.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Shipper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(to='gl.Counterparty')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_code', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
                ('shipper', models.ForeignKey(to='inventory.Shipper')),
            ],
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='bill_to',
            field=models.CharField(default=b'missing', max_length=100),
        ),
        migrations.AddField(
            model_name='channelshipmenttypes',
            name='ship_type',
            field=models.ForeignKey(to='inventory.ShippingType'),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='ship_type',
            field=models.ForeignKey(blank=True, to='inventory.ShippingType', null=True),
        ),
    ]
