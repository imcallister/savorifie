# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_auto_20160512_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='shipping_type',
            field=models.ForeignKey(blank=True, to='inventory.ShippingType', null=True),
        ),
    ]
