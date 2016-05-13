# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

from accountifie.common.api import api_func

DEFAULT_SHIPTYPE = api_func('inventory', 'shippingtype', 'UPS_GROUND').get('id')

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_auto_20160512_1734'),
        ('base', '0016_auto_20160509_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='inventory.ShippingType', null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_type',
            field=models.ForeignKey(default=DEFAULT_SHIPTYPE, to='inventory.ShippingType'),
            preserve_default=False,
        ),
    ]
