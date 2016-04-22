# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_inventoryitem_master_sku'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SKU',
            new_name='Product',
        ),
        migrations.AlterModelTable(
            name='product',
            table='inventory_product',
        ),
    ]
