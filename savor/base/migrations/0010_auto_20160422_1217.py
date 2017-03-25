# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20160422_0854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalsale',
            old_name='shipping',
            new_name='shipping_charge',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='shipping',
            new_name='shipping_charge',
        ),
    ]
