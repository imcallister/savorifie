# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20160617_2125'),
        ('inventory', '0032_auto_20160622_0812'),
    ]

    operations = [
        migrations.CreateModel(
            name='COGSAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField()),
                ('shipment_line', models.ForeignKey(to='inventory.ShipmentLine')),
                ('unit_sale', models.ForeignKey(to='base.UnitSale', blank=True)),
            ],
            options={
                'db_table': 'accounting_cogsassignment',
            },
        ),
    ]
