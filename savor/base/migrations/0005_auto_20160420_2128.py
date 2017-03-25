# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20160417_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='gift_wrap_fee',
            field=models.DecimalField(default=Decimal('0'), max_digits=6, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='gift_wrapping',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sale',
            name='gift_wrap_fee',
            field=models.DecimalField(default=Decimal('0'), max_digits=6, decimal_places=2),
        ),
        migrations.AddField(
            model_name='sale',
            name='gift_wrapping',
            field=models.BooleanField(default=False),
        ),
    ]
