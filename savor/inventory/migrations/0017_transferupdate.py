# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_auto_20160426_2249'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_date', models.DateField()),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
                ('status', models.CharField(max_length=30, choices=[(b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')])),
                ('tracking_number', models.CharField(max_length=100, null=True, blank=True)),
                ('shipper', models.ForeignKey(blank=True, to='inventory.Shipper', null=True)),
                ('transfer', models.ForeignKey(to='inventory.InventoryTransfer')),
            ],
            options={
                'db_table': 'inventory_transferupdate',
            },
        ),
    ]
