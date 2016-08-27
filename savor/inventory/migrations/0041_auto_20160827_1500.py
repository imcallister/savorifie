# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0040_auto_20160824_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehousefulfill',
            name='weight',
            field=models.DecimalField(null=True, max_digits=12, decimal_places=6, blank=True),
        ),
    ]
