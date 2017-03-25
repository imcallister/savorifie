# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20160422_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='gift_message',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='gift_message',
            field=models.TextField(null=True, blank=True),
        ),
    ]
