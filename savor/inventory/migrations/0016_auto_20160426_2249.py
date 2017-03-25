# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_auto_20160425_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelshipmenttype',
            name='packing_type',
            field=models.CharField(default=b'box', max_length=30, choices=[(b'box', b'box'), (b'pouch', b'pouch')]),
        ),
        migrations.AddField(
            model_name='channelshipmenttype',
            name='use_pdf',
            field=models.BooleanField(default=False),
        ),
    ]
