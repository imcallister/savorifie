# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('sales', '0008_auto_20161027_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelpayouts',
            name='paid_thru',
            field=models.ForeignKey(related_name='payout_paid_thru', blank=True, to='gl.Counterparty', null=True),
        ),
    ]
