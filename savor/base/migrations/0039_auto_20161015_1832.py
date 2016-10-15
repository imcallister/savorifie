# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0038_auto_20160904_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcardtrans',
            name='acct_payable',
            field=models.ForeignKey(related_name='ccard_ap_acct', default=b'3000', to='gl.Account'),
        ),
        migrations.AddField(
            model_name='historicalcreditcardtrans',
            name='acct_payable',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True),
        ),
    ]
