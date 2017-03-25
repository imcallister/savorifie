# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0036_auto_20160727_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fulfillment',
            name='order',
            field=models.ForeignKey(related_name='fulfillments', to='base.Sale'),
        ),
        migrations.AlterField(
            model_name='fulfillment',
            name='status',
            field=models.CharField(max_length=20, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')]),
        ),
        migrations.AlterField(
            model_name='fulfillment',
            name='warehouse',
            field=models.ForeignKey(blank=True, to='inventory.Warehouse', null=True),
        ),
        migrations.AlterField(
            model_name='fulfillupdate',
            name='status',
            field=models.CharField(max_length=30, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')]),
        ),
        migrations.AlterField(
            model_name='transferupdate',
            name='status',
            field=models.CharField(max_length=30, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')]),
        ),
        migrations.AlterField(
            model_name='warehousefulfillline',
            name='warehouse_fulfill',
            field=models.ForeignKey(related_name='fulfill_lines', to='inventory.WarehouseFulfill'),
        ),
    ]
