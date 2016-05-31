# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import accountifie.gl.bmo
import accountifie.toolkit.utils.gl_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0019_auto_20160513_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditCardTrans',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trans_date', models.DateField()),
                ('post_date', models.DateField()),
                ('trans_type', models.CharField(max_length=20, null=True)),
                ('trans_id', models.CharField(max_length=50, null=True)),
                ('amount', models.FloatField(null=True)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('payee', models.TextField(max_length=200, null=True, blank=True)),
                ('card_number', models.CharField(max_length=20, null=True, blank=True)),
                ('card_company', models.ForeignKey(related_name='card_company', to='gl.Counterparty')),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('counterparty', models.ForeignKey(related_name='counterparty', to='gl.Counterparty')),
            ],
            options={
                'db_table': 'base_creditcardtransactions',
                'verbose_name': 'Credit Card Transaction',
                'verbose_name_plural': 'Credit Card Transactions',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.RemoveField(
            model_name='amex',
            name='company',
        ),
        migrations.RemoveField(
            model_name='amex',
            name='counterparty',
        ),
        migrations.RemoveField(
            model_name='historicalamex',
            name='company',
        ),
        migrations.RemoveField(
            model_name='historicalamex',
            name='counterparty',
        ),
        migrations.RemoveField(
            model_name='historicalamex',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalmcard',
            name='company',
        ),
        migrations.RemoveField(
            model_name='historicalmcard',
            name='counterparty',
        ),
        migrations.RemoveField(
            model_name='historicalmcard',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='mcard',
            name='company',
        ),
        migrations.RemoveField(
            model_name='mcard',
            name='counterparty',
        ),
        migrations.DeleteModel(
            name='AMEX',
        ),
        migrations.DeleteModel(
            name='HistoricalAMEX',
        ),
        migrations.DeleteModel(
            name='HistoricalMcard',
        ),
        migrations.DeleteModel(
            name='Mcard',
        ),
    ]
