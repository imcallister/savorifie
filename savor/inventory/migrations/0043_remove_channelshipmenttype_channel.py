# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0042_auto_20160904_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channelshipmenttype',
            name='channel',
        ),
    ]
