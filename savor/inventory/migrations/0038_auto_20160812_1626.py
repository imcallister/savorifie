# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0037_auto_20160805_0821'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousefulfill',
            name='fulfillment',
            field=models.ForeignKey(blank=True, to='inventory.Fulfillment', null=True),
        ),
        migrations.AlterField(
            model_name='fulfillment',
            name='status',
            field=models.CharField(max_length=20, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')]),
        ),
        migrations.AlterField(
            model_name='fulfillupdate',
            name='status',
            field=models.CharField(max_length=30, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')]),
        ),
        migrations.AlterField(
            model_name='transferupdate',
            name='status',
            field=models.CharField(max_length=30, choices=[(b'back-ordered', b'back-ordered'), (b'requested', b'requested'), (b'partial', b'partial'), (b'mismatched', b'mismatched'), (b'completed', b'completed')]),
        ),
    ]
