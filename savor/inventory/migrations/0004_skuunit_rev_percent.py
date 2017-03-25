# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20160415_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='skuunit',
            name='rev_percent',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
