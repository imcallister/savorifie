# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20160617_2125'),
        ('inventory', '0030_auto_20160620_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fifoassignment',
            name='sale',
        ),
        migrations.RemoveField(
            model_name='fifoassignment',
            name='sku',
        ),
        migrations.AddField(
            model_name='fifoassignment',
            name='unit_sale',
            field=models.ForeignKey(default=None, blank=True, to='base.UnitSale'),
            preserve_default=False,
        ),
    ]
