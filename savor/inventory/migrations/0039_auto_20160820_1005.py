# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0038_auto_20160812_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousefulfill',
            name='handling_cost',
            field=models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='shipping_cost',
            field=models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='warehousefulfill',
            name='weight',
            field=models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True),
        ),
    ]
