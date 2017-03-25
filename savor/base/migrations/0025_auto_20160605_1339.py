# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_auto_20160529_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='external_channel_id',
            field=models.CharField(default='none', max_length=50, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalsale',
            name='external_ref',
            field=models.CharField(help_text=b'for tracking enduser POs', max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_channel_id',
            field=models.CharField(default='missing', unique=True, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_ref',
            field=models.CharField(help_text=b'for tracking enduser POs', max_length=50, null=True, blank=True),
        ),
    ]
