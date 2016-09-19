# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_channelpayouts'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelpayouts',
            name='payout',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
            preserve_default=False,
        ),
    ]
