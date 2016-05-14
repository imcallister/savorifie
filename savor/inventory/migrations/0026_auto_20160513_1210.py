# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_auto_20160512_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fulfillment',
            name='bill_to',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
