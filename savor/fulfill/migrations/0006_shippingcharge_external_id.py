# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fulfill', '0005_shippingcharge_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingcharge',
            name='external_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
