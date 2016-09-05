# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import accountifie.toolkit.utils.gl_helpers
from decimal import Decimal
import django.db.models.deletion
from django.conf import settings
import accountifie.gl.bmo


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0042_auto_20160904_0000'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
        ('gl', '0002_transaction_bmo_id'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=20)),
                ('counterparty', models.ForeignKey(to='gl.Counterparty')),
            ],
            options={
                'db_table': 'base_channel',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSale',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('sale_date', models.DateField()),
                ('external_channel_id', models.CharField(help_text=b'If no ID, leave blank for system-generated ID', max_length=50, null=True, db_index=True, blank=True)),
                ('external_routing_id', models.CharField(max_length=50, null=True, blank=True)),
                ('special_sale', models.CharField(blank=True, max_length=20, null=True, choices=[(b'press', b'Press Sample'), (b'consignment', b'Consignment'), (b'prize', b'Gift/Prize'), (b'retailer', b'Retailer Sample')])),
                ('shipping_charge', models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2)),
                ('discount', models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True)),
                ('discount_code', models.CharField(max_length=50, null=True, blank=True)),
                ('notification_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('memo', models.TextField(null=True, blank=True)),
                ('gift_wrapping', models.BooleanField(default=False)),
                ('gift_wrap_fee', models.DecimalField(default=Decimal('0'), max_digits=6, decimal_places=2)),
                ('gift_message', models.TextField(null=True, blank=True)),
                ('shipping_name', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_company', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address1', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address2', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_city', models.CharField(max_length=50, null=True, blank=True)),
                ('shipping_zip', models.CharField(max_length=20, null=True, blank=True)),
                ('shipping_province', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_country', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_phone', models.CharField(max_length=30, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('channel', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='sales.Channel', null=True)),
                ('company', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True)),
                ('customer_code', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Counterparty', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('ship_type', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='inventory.ChannelShipmentType', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical sale',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sale_date', models.DateField()),
                ('external_channel_id', models.CharField(help_text=b'If no ID, leave blank for system-generated ID', max_length=50, unique=True, null=True, blank=True)),
                ('external_routing_id', models.CharField(max_length=50, null=True, blank=True)),
                ('special_sale', models.CharField(blank=True, max_length=20, null=True, choices=[(b'press', b'Press Sample'), (b'consignment', b'Consignment'), (b'prize', b'Gift/Prize'), (b'retailer', b'Retailer Sample')])),
                ('shipping_charge', models.DecimalField(default=Decimal('0'), max_digits=11, decimal_places=2)),
                ('discount', models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True)),
                ('discount_code', models.CharField(max_length=50, null=True, blank=True)),
                ('notification_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('memo', models.TextField(null=True, blank=True)),
                ('gift_wrapping', models.BooleanField(default=False)),
                ('gift_wrap_fee', models.DecimalField(default=Decimal('0'), max_digits=6, decimal_places=2)),
                ('gift_message', models.TextField(null=True, blank=True)),
                ('shipping_name', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_company', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address1', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_address2', models.CharField(max_length=100, null=True, blank=True)),
                ('shipping_city', models.CharField(max_length=50, null=True, blank=True)),
                ('shipping_zip', models.CharField(max_length=20, null=True, blank=True)),
                ('shipping_province', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_country', models.CharField(max_length=30, null=True, blank=True)),
                ('shipping_phone', models.CharField(max_length=30, null=True, blank=True)),
                ('channel', models.ForeignKey(blank=True, to='sales.Channel', null=True)),
                ('company', models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company')),
                ('customer_code', models.ForeignKey(blank=True, to='gl.Counterparty', null=True)),
                ('ship_type', models.ForeignKey(default=None, blank=True, to='inventory.ChannelShipmentType', null=True)),
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
                ('sale', models.ForeignKey(related_name='unit_sale', to='sales.Sale')),
                ('sku', models.ForeignKey(blank=True, to='products.Product', null=True)),
            ],
            options={
                'db_table': 'base_unitsale',
            },
        ),
        migrations.AddField(
            model_name='salestax',
            name='collector',
            field=models.ForeignKey(to='sales.TaxCollector'),
        ),
        migrations.AddField(
            model_name='salestax',
            name='sale',
            field=models.ForeignKey(to='sales.Sale'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
