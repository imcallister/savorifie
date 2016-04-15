# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SKUUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'inventory_skuunit',
            },
        ),
        migrations.RemoveField(
            model_name='sku',
            name='items',
        ),
        migrations.AddField(
            model_name='skuunit',
            name='sku',
            field=models.ForeignKey(to='inventory.SKU'),
        ),
    ]
