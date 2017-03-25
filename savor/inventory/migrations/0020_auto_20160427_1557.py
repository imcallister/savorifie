# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_auto_20160427_1553'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryitem',
            old_name='short_code',
            new_name='label',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='short_code',
            new_name='label',
        ),
        migrations.RenameField(
            model_name='productline',
            old_name='short_code',
            new_name='label',
        ),
    ]
