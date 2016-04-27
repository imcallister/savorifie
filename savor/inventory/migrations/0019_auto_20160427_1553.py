# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_remove_transferline_cost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channelshipmenttype',
            old_name='short_code',
            new_name='label',
        ),
        migrations.RenameField(
            model_name='shipment',
            old_name='short_code',
            new_name='label',
        ),
        migrations.RenameField(
            model_name='shippingtype',
            old_name='short_code',
            new_name='label',
        ),
        migrations.RenameField(
            model_name='warehouse',
            old_name='short_code',
            new_name='label',
        ),
    ]
