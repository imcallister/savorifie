# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20160422_1554'),
        ('inventory', '0013_auto_20160424_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelShipmentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_code', models.CharField(max_length=30)),
                ('bill_to', models.CharField(max_length=100)),
                ('channel', models.ForeignKey(to='base.Channel')),
                ('ship_type', models.ForeignKey(to='inventory.ShippingType')),
            ],
        ),
        migrations.RemoveField(
            model_name='channelshipmenttypes',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='channelshipmenttypes',
            name='ship_type',
        ),
        migrations.DeleteModel(
            name='ChannelShipmentTypes',
        ),
    ]
