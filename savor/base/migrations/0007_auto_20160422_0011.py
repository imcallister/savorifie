# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20160421_2358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsale',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='customer_code',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='customer_code',
        ),
    ]
