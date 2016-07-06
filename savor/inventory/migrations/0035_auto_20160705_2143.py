# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_address'),
        ('inventory', '0034_shipment_sent_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelshipmenttype',
            name='ship_from',
            field=models.ForeignKey(blank=True, to='common.Address', null=True),
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='ship_from',
            field=models.ForeignKey(blank=True, to='common.Address', null=True),
        ),
    ]
