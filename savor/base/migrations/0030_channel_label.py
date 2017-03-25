# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_auto_20160630_0825'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='label',
            field=models.CharField(default='SAV', max_length=20),
            preserve_default=False,
        ),
    ]
