# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_fifoassignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fifoassignment',
            name='sku',
            field=models.ForeignKey(to='inventory.InventoryItem'),
        ),
    ]
