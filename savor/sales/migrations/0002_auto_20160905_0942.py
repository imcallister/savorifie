# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsale',
            name='ship_type',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='ship_type',
        ),
    ]
