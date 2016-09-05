# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_auto_20160904_0000'),
        ('inventory', '0042_auto_20160904_0000'),
        ('accounting', '0002_auto_20160904_0000'),
    ]

    state_operations = [
        migrations.DeleteModel(
            name='Channel',
        ),
        migrations.DeleteModel(
            name='HistoricalSale',
        ),
        migrations.DeleteModel(
            name='Sale',
        ),
        migrations.DeleteModel(
            name='SalesTax',
        ),
        migrations.DeleteModel(
            name='TaxCollector',
        ),
        migrations.DeleteModel(
            name='UnitSale',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
