# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_auto_20160512_1734'),
        ('base', '0018_auto_20160512_1740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsale',
            name='shipping_code',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='shipping_type',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='shipping_code',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='shipping_type',
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='ship_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='inventory.ChannelShipmentType', null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='ship_type',
            field=models.ForeignKey(default=None, blank=True, to='inventory.ChannelShipmentType', null=True),
        ),
    ]
