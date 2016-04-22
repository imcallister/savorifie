# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('base', '0005_auto_20160420_2128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('counterparty', models.ForeignKey(to='gl.Counterparty')),
            ],
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='external_routing_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='gift_message',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='notification_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_address1',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_address2',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_city',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_company',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_country',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_phone',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_province',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalsale',
            name='shipping_zip',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='external_routing_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='gift_message',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='notification_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_address1',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_address2',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_city',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_company',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_country',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_phone',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_province',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='shipping_zip',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        
    ]
