# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_auto_20160824_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='shipping_charge',
            field=models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='sale',
            name='shipping_charge',
            field=models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2),
        ),
    ]
