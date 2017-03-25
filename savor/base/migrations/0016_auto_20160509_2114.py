# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20160503_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_code',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_code',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
