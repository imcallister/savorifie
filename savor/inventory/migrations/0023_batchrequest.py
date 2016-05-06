# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_auto_20160430_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateField()),
                ('fulfillments', models.ManyToManyField(to='inventory.Fulfillment', blank=True)),
                ('location', models.ForeignKey(to='inventory.Warehouse')),
            ],
            options={
                'db_table': 'inventory_batchrequest',
            },
        ),
    ]
