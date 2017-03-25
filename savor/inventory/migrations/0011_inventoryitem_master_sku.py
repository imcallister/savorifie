# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_auto_20160417_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='master_sku',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
