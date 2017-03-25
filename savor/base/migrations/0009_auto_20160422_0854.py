# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20160422_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='external_channel_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='external_channel_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
