# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_batchrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchrequest',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
    ]
