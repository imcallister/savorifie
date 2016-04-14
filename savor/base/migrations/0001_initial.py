# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import accountifie.toolkit.utils.gl_helpers
import accountifie.gl.bmo


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AMEX',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('amount', models.FloatField(null=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', help_text=b'We need to match this up', null=True)),
            ],
            options={
                'db_table': 'base_amex',
                'verbose_name': 'AMEX Transaction',
                'verbose_name_plural': 'AMEX Transactions',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='Cashflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_date', models.DateField()),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('description', models.TextField(max_length=200, null=True)),
                ('external_id', models.CharField(max_length=20, null=True)),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', help_text=b'We need to match this up', null=True)),
                ('ext_account', models.ForeignKey(to='gl.ExternalAccount')),
                ('trans_type', models.ForeignKey(blank=True, to='gl.Account', help_text=b'We need to match this up', null=True)),
            ],
            options={
                'db_table': 'base_cashflow',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='CashflowAllocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
                ('cashflow', models.ForeignKey(to='base.Cashflow')),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', help_text=b'We need to match this up', null=True)),
                ('project', models.ForeignKey(blank=True, to='gl.Project', null=True)),
                ('trans_type', models.ForeignKey(blank=True, to='gl.Account', help_text=b'We need to match this up', null=True)),
            ],
            options={
                'db_table': 'base_cashflowallocation',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expense_date', models.DateField(null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=11, decimal_places=2)),
                ('currency', models.CharField(default=b'USD', max_length=10)),
                ('process_date', models.DateField(null=True)),
                ('stub', models.BooleanField(default=False, help_text=b'incomplete, created from cashflow')),
                ('comment', models.CharField(help_text=b'Details of any modifications/notes added in Django', max_length=200, null=True, blank=True)),
                ('account', models.ForeignKey(to='gl.Account')),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', help_text=b'We need to match this up', null=True)),
                ('employee', models.ForeignKey(to='gl.Employee', null=True)),
                ('from_cf', models.ForeignKey(blank=True, to='base.Cashflow', help_text=b'created from cashflow', null=True)),
                ('paid_from', models.ForeignKey(related_name='paid_from', blank=True, to='gl.Account', help_text=b'shows the account this was paid from, or is owed to', null=True)),
            ],
            options={
                'db_table': 'base_expense',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='ExpenseAllocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('expense', models.ForeignKey(to='base.Expense')),
                ('project', models.ForeignKey(to='gl.Project')),
            ],
            options={
                'db_table': 'base_expenseallocation',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAMEX',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('date', models.DateField()),
                ('amount', models.FloatField(null=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical AMEX Transaction',
            },
        ),
        migrations.CreateModel(
            name='HistoricalCashflow',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('post_date', models.DateField()),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('description', models.TextField(max_length=200, null=True)),
                ('external_id', models.CharField(max_length=20, null=True)),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('ext_account', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.ExternalAccount', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('trans_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical cashflow',
            },
        ),
        migrations.CreateModel(
            name='HistoricalCashflowAllocation',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('tag', models.CharField(max_length=30, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('cashflow', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='base.Cashflow', null=True)),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Project', null=True)),
                ('trans_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical cashflow allocation',
            },
        ),
        migrations.CreateModel(
            name='HistoricalExpense',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('expense_date', models.DateField(null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=11, decimal_places=2)),
                ('currency', models.CharField(default=b'USD', max_length=10)),
                ('process_date', models.DateField(null=True)),
                ('stub', models.BooleanField(default=False, help_text=b'incomplete, created from cashflow')),
                ('comment', models.CharField(help_text=b'Details of any modifications/notes added in Django', max_length=200, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('account', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True)),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('employee', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Employee', null=True)),
                ('from_cf', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='base.Cashflow', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('paid_from', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical expense',
            },
        ),
        migrations.CreateModel(
            name='HistoricalMcard',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('trans_date', models.DateField()),
                ('post_date', models.DateField()),
                ('type', models.CharField(max_length=200, null=True)),
                ('amount', models.FloatField(null=True)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('card_number', models.CharField(max_length=20, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('counterparty', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical Mastercard Transaction',
            },
        ),
        migrations.CreateModel(
            name='HistoricalNominalTransaction',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('date', models.DateField(db_index=True)),
                ('date_end', models.DateField(db_index=True, null=True, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('comment', models.CharField(default=b'None', max_length=200)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('content_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='contenttypes.ContentType', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical nominal transaction',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSale',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('sale_date', models.DateField()),
                ('external_ref', models.CharField(max_length=50, null=True)),
                ('shipping', models.DecimalField(max_digits=11, decimal_places=2)),
                ('discount', models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True)),
                ('discount_code', models.CharField(max_length=50, null=True, blank=True)),
                ('channel', models.CharField(max_length=25, choices=[[b'shopify', b'Shopify']])),
                ('customer_code', models.CharField(max_length=100)),
                ('memo', models.CharField(max_length=200, null=True)),
                ('fulfill_status', models.CharField(max_length=25, choices=[[b'unfulfilled', b'Unfulfilled'], [b'fulfilled', b'Fulfilled']])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical sale',
            },
        ),
        migrations.CreateModel(
            name='HistoricalStockEntry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('date', models.DateField()),
                ('quantity', models.IntegerField()),
                ('share_class', models.CharField(max_length=20, choices=[[b'common', b'Common Stock'], [b'series_A1', b'Series A-1 Preferreds']])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('gl_acct', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Account', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical stock entry',
            },
        ),
        migrations.CreateModel(
            name='Mcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trans_date', models.DateField()),
                ('post_date', models.DateField()),
                ('type', models.CharField(max_length=200, null=True)),
                ('amount', models.FloatField(null=True)),
                ('description', models.TextField(max_length=200, null=True, blank=True)),
                ('card_number', models.CharField(max_length=20, null=True, blank=True)),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('counterparty', models.ForeignKey(blank=True, to='gl.Counterparty', help_text=b'We need to match this up', null=True)),
            ],
            options={
                'db_table': 'base_mcard',
                'verbose_name': 'Mastercard Transaction',
                'verbose_name_plural': 'Mastercard Transactions',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='NominalTranLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('account', models.ForeignKey(to='gl.Account')),
                ('counterparty', models.ForeignKey(to='gl.Counterparty')),
            ],
            options={
                'db_table': 'base_nominaltranline',
            },
        ),
        migrations.CreateModel(
            name='NominalTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(db_index=True)),
                ('date_end', models.DateField(db_index=True, null=True, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('comment', models.CharField(default=b'None', max_length=200)),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'db_table': 'base_nominaltransaction',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=50)),
                ('short_code', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'base_product',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sale_date', models.DateField()),
                ('external_ref', models.CharField(max_length=50, null=True)),
                ('shipping', models.DecimalField(max_digits=11, decimal_places=2)),
                ('discount', models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True)),
                ('discount_code', models.CharField(max_length=50, null=True, blank=True)),
                ('channel', models.CharField(max_length=25, choices=[[b'shopify', b'Shopify']])),
                ('customer_code', models.CharField(max_length=100)),
                ('memo', models.CharField(max_length=200, null=True)),
                ('fulfill_status', models.CharField(max_length=25, choices=[[b'unfulfilled', b'Unfulfilled'], [b'fulfilled', b'Fulfilled']])),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
            ],
            options={
                'db_table': 'base_sale',
            },
            bases=(models.Model, accountifie.gl.bmo.BusinessModelObject),
        ),
        migrations.CreateModel(
            name='SalesTax',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tax', models.DecimalField(max_digits=11, decimal_places=2)),
            ],
            options={
                'db_table': 'base_salestax',
            },
        ),
        migrations.CreateModel(
            name='StockEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('quantity', models.IntegerField()),
                ('share_class', models.CharField(max_length=20, choices=[[b'common', b'Common Stock'], [b'series_A1', b'Series A-1 Preferreds']])),
                ('gl_acct', models.ForeignKey(to='gl.Account')),
            ],
            options={
                'db_table': 'base_stockentry',
            },
        ),
        migrations.CreateModel(
            name='TaxCollector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'base_taxcollector',
            },
        ),
        migrations.CreateModel(
            name='UnitSale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('unit_price', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('product', models.ForeignKey(to='base.Product')),
                ('sale', models.ForeignKey(to='base.Sale')),
            ],
            options={
                'db_table': 'base_unitsale',
            },
        ),
        migrations.AddField(
            model_name='salestax',
            name='collector',
            field=models.ForeignKey(to='base.TaxCollector'),
        ),
        migrations.AddField(
            model_name='salestax',
            name='sale',
            field=models.ForeignKey(to='base.Sale'),
        ),
        migrations.AddField(
            model_name='nominaltranline',
            name='transaction',
            field=models.ForeignKey(to='base.NominalTransaction'),
        ),
    ]
