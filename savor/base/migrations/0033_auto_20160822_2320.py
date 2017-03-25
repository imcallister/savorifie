# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_auto_20160812_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsale',
            name='external_ref',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='external_ref',
        ),
    ]
