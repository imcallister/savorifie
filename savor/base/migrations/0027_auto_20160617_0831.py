# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0026_auto_20160616_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashflow',
            name='expense_acct',
            field=models.ForeignKey(related_name='expense_acct', blank=True, to='gl.Account', help_text=b'Optional. For related expense created from Credit Card Trans', null=True),
        ),
        migrations.AddField(
            model_name='historicalcashflow',
            name='expense_acct',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True),
        ),
        migrations.AlterField(
            model_name='creditcardtrans',
            name='expense_acct',
            field=models.ForeignKey(blank=True, to='gl.Account', help_text=b'Optional. For related expense created from Credit Card Trans', null=True),
        ),
    ]
