# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0036_auto_20160824_1432'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='channel',
            name='counterparty',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='company',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='customer_code',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalsale',
            name='ship_type',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='company',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='customer_code',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='ship_type',
        ),
        migrations.RemoveField(
            model_name='salestax',
            name='collector',
        ),
        migrations.RemoveField(
            model_name='salestax',
            name='sale',
        ),
        migrations.RemoveField(
            model_name='unitsale',
            name='sale',
        ),
        migrations.RemoveField(
            model_name='unitsale',
            name='sku',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
