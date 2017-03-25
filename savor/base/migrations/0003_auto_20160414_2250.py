# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('base', '0002_auto_20160302_2229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitsale',
            name='product',
        ),
        migrations.AddField(
            model_name='unitsale',
            name='sku',
            field=models.ForeignKey(blank=True, to='inventory.SKU', null=True),
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
