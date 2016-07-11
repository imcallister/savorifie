# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0025_auto_20160605_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcardtrans',
            name='expense_acct',
            field=models.ForeignKey(blank=True, to='gl.Account', null=True),
        ),
        migrations.AddField(
            model_name='historicalcreditcardtrans',
            name='expense_acct',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True),
        ),
    ]
