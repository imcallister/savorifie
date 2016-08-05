# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_channel_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitsale',
            name='sale',
            field=models.ForeignKey(related_name='unit_sale', to='base.Sale'),
        ),
    ]
