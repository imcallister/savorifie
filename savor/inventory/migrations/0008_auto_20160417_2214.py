# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20160416_1834'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('cost', models.DecimalField(default=0, max_digits=6, decimal_places=2)),
                ('inventory_item', models.ForeignKey(blank=True, to='inventory.InventoryItem', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='inventoryline',
            name='inventory_item',
        ),
        migrations.RemoveField(
            model_name='inventorytransfer',
            name='picking_list',
        ),
        migrations.DeleteModel(
            name='InventoryLine',
        ),
        migrations.AddField(
            model_name='transferline',
            name='transfer',
            field=models.ForeignKey(to='inventory.InventoryTransfer'),
        ),
    ]
