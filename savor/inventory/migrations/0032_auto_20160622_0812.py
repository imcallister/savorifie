# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0031_auto_20160621_0818'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fifoassignment',
            name='shipment_line',
        ),
        migrations.RemoveField(
            model_name='fifoassignment',
            name='unit_sale',
        ),
        migrations.DeleteModel(
            name='FIFOAssignment',
        ),
    ]
