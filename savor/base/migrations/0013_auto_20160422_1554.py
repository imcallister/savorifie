# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20160422_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='memo',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='memo',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
