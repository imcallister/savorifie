# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_auto_20160805_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsale',
            name='special_sale',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'press', b'Press Sample'), (b'consignment', b'Consignment'), (b'prize', b'Gift/Prize'), (b'retailer', b'Retailer Sample')]),
        ),
        migrations.AlterField(
            model_name='sale',
            name='special_sale',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'press', b'Press Sample'), (b'consignment', b'Consignment'), (b'prize', b'Gift/Prize'), (b'retailer', b'Retailer Sample')]),
        ),
    ]
