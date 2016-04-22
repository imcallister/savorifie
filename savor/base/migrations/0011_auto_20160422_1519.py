# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20160422_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='external_channel_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalsale',
            name='external_ref',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalsale',
            name='external_routing_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_channel_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_ref',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='external_routing_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
