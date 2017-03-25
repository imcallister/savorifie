# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_auto_20160822_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='external_channel_id',
            field=models.CharField(db_index=True, max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_channel_id',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
    ]
