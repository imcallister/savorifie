# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_auto_20160926_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='is_return',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sale',
            name='is_return',
            field=models.BooleanField(default=False),
        ),
    ]
