# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_shipment_shipmentline'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipmentline',
            name='cost',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
    ]
