# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20160617_2125'),
        ('inventory', '0028_auto_20160530_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='FIFOAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField()),
                ('sale', models.ForeignKey(to='base.Sale', blank=True)),
                ('shipment_line', models.ForeignKey(to='inventory.ShipmentLine')),
                ('sku', models.ForeignKey(to='inventory.SKUUnit')),
            ],
            options={
                'db_table': 'inventory_fifoassignment',
            },
        ),
    ]
