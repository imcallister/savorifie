# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_batchrequest_comment'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='shippingtype',
            table='inventory_shippingtype',
        ),
    ]
