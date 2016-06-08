# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0027_auto_20160513_2032'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='channelshipmenttype',
            table='inventory_channelshipmenttype',
        ),
        migrations.AlterModelTable(
            name='inventorytransfer',
            table='inventory_inventorytransfer',
        ),
        migrations.AlterModelTable(
            name='shipper',
            table='inventory_shipper',
        ),
        migrations.AlterModelTable(
            name='transferline',
            table='inventory_transferline',
        ),
        migrations.AlterModelTable(
            name='warehousefulfill',
            table='inventory_warehousefulfill',
        ),
        migrations.AlterModelTable(
            name='warehousefulfillline',
            table='inventory_warehousefulfillline',
        ),
    ]
