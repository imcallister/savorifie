# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_auto_20160617_0831'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsale',
            name='special_sale',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'PRESS', b'Press Sample'), (b'GIFT', b'Gift/Prize'), (b'RET_SAMPLE', b'Returnable Sample'), (b'NONRET_SAMPLE', b'Non-returnable Sample')]),
        ),
        migrations.AddField(
            model_name='sale',
            name='special_sale',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'PRESS', b'Press Sample'), (b'GIFT', b'Gift/Prize'), (b'RET_SAMPLE', b'Returnable Sample'), (b'NONRET_SAMPLE', b'Non-returnable Sample')]),
        ),
    ]
