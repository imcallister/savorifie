# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fulfill', '0002_shippingcharge'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingcharge',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='shippingcharge',
            name='order_related',
            field=models.BooleanField(default=True),
        ),
    ]
