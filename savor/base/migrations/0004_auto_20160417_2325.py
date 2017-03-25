# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20160414_2250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsale',
            name='fulfill_status',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='fulfill_status',
        ),
    ]
