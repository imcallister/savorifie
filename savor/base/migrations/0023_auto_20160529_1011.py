# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0022_auto_20160527_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcardtrans',
            name='expense_account',
            field=models.ForeignKey(blank=True, to='gl.Account', null=True),
        ),
        migrations.AddField(
            model_name='creditcardtrans',
            name='expense_comment',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='from_ccard',
            field=models.ForeignKey(blank=True, to='base.CreditCardTrans', help_text=b'created from credit card trans', null=True),
        ),
        migrations.AddField(
            model_name='historicalcreditcardtrans',
            name='expense_account',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True),
        ),
        migrations.AddField(
            model_name='historicalcreditcardtrans',
            name='expense_comment',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalexpense',
            name='from_ccard',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='base.CreditCardTrans', null=True),
        ),
        migrations.AlterField(
            model_name='creditcardtrans',
            name='description',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='expense',
            name='stub',
            field=models.BooleanField(default=False, help_text=b'incomplete, created from cashflow or credit card'),
        ),
        migrations.AlterField(
            model_name='historicalcreditcardtrans',
            name='description',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalexpense',
            name='stub',
            field=models.BooleanField(default=False, help_text=b'incomplete, created from cashflow or credit card'),
        ),
    ]
