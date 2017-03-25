# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_auto_20160824_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='external_channel_id',
            field=models.CharField(help_text=b'If no ID, leave blank for system-generated ID', max_length=50, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_channel_id',
            field=models.CharField(help_text=b'If no ID, leave blank for system-generated ID', max_length=50, unique=True, null=True, blank=True),
        ),
    ]
