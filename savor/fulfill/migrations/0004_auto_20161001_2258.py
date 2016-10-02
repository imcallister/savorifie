# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fulfill', '0003_auto_20160914_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehousefulfill',
            name='fulfillment',
            field=models.ForeignKey(related_name='warehousefulfill', blank=True, to='fulfill.Fulfillment', null=True),
        ),
    ]
