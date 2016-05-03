# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20160503_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='memo',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sale',
            name='memo',
            field=models.TextField(null=True, blank=True),
        ),
    ]
