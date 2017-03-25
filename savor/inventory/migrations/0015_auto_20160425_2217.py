# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_auto_20160425_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='fulfillupdate',
            name='shipper',
            field=models.ForeignKey(blank=True, to='inventory.Shipper', null=True),
        ),
        migrations.AddField(
            model_name='fulfillupdate',
            name='tracking_number',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
