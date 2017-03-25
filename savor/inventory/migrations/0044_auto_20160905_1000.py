# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0043_remove_channelshipmenttype_channel'),
        ('sales', '0002_auto_20160905_0942'),
    ]

    operations = [
        migrations.RenameModel("ChannelShipmentType", "ShipOption")
    ]
