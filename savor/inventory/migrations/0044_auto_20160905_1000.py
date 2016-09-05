# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0043_remove_channelshipmenttype_channel'),
    ]

    operations = [
        migrations.RenameModel("ChannelShipmentType", "ShipOption")
    ]
