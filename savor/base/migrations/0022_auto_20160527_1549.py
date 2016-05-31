# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_historicalcreditcardtrans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcardtrans',
            name='counterparty',
            field=models.ForeignKey(related_name='counterparty', blank=True, to='gl.Counterparty', null=True),
        ),
        migrations.AlterField(
            model_name='creditcardtrans',
            name='payee',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='creditcardtrans',
            name='trans_id',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalcreditcardtrans',
            name='payee',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalcreditcardtrans',
            name='trans_id',
            field=models.CharField(max_length=50, null=True, db_index=True),
        ),
    ]
