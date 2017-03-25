# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_transferupdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transferline',
            name='cost',
        ),
    ]
