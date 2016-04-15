# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20160415_0818'),
    ]

    operations = [
        migrations.AddField(
            model_name='skuunit',
            name='inventory_item',
            field=models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True),
        ),
        migrations.AlterField(
            model_name='skuunit',
            name='sku',
            field=models.ForeignKey(blank=True, to='inventory.SKU', null=True),
        ),
    ]
