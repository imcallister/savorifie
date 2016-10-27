# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('sales', '0007_auto_20161001_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='paid_thru',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='paid_thru',
            field=models.ForeignKey(related_name='paid_thru', blank=True, to='gl.Counterparty', null=True),
        ),
    ]
