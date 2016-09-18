# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20160905_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='channel_charges',
            field=models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2),
        ),
        migrations.AddField(
            model_name='sale',
            name='channel_charges',
            field=models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2),
        ),
    ]
