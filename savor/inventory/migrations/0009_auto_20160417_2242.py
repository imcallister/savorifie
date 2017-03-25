# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20160414_2250'),
        ('inventory', '0008_auto_20160417_2214'),
    ]

    operations = [
        migrations.CreateModel(
            name='FulfillLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'inventory_fulfillline',
            },
        ),
        migrations.CreateModel(
            name='Fulfillment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_date', models.DateField()),
                ('status', models.CharField(max_length=30, choices=[(b'requested', b'requested'), (b'completed', b'completed')])),
                ('order', models.ForeignKey(to='base.Sale')),
            ],
            options={
                'db_table': 'inventory_fulfillment',
            },
        ),
        migrations.AlterModelTable(
            name='warehouse',
            table='inventory_warehouse',
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='warehouse',
            field=models.ForeignKey(to='inventory.Warehouse'),
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='fulfillment',
            field=models.ForeignKey(to='inventory.Fulfillment'),
        ),
        migrations.AddField(
            model_name='fulfillline',
            name='inventory_item',
            field=models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True),
        ),
    ]
