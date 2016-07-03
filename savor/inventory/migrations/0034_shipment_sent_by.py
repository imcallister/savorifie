# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('inventory', '0033_shipmentline_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='sent_by',
            field=models.ForeignKey(default='SAV', to='gl.Counterparty'),
            preserve_default=False,
        ),
    ]
