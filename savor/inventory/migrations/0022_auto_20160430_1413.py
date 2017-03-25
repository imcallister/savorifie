# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_warehousefulfill_warehousefulfillline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehousefulfill',
            name='shipping_code',
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='shipping_type',
            field=models.ForeignKey(blank=True, to='inventory.ShippingType', null=True),
        ),
    ]
