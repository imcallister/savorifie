# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0020_auto_20160527_0838'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalCreditCardTrans',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('trans_date', models.DateField()),
                ('post_date', models.DateField()),
                ('trans_type', models.CharField(max_length=20, null=True)),
                ('trans_id', models.CharField(max_length=50, null=True)),
                ('amount', models.FloatField(null=True)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('payee', models.TextField(max_length=200, null=True, blank=True)),
                ('card_number', models.CharField(max_length=20, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('card_company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical Credit Card Transaction',
            },
        ),
    ]
