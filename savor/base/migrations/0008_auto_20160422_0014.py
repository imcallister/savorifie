# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0007_auto_20160422_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='channel',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='base.Channel', null=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='customer_code',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='channel',
            field=models.ForeignKey(blank=True, to='base.Channel', null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='customer_code',
            field=models.ForeignKey(blank=True, to='gl.Counterparty', null=True),
        ),
    ]
