# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-03-25 21:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0015_auto_20170325_1707'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='channel',
            table='sales_channel',
        ),
        migrations.AlterModelTable(
            name='payout',
            table='sales_payout',
        ),
        migrations.AlterModelTable(
            name='sale',
            table='sales_sale',
        ),
        migrations.AlterModelTable(
            name='salestax',
            table='sales_salestax',
        ),
        migrations.AlterModelTable(
            name='taxcollector',
            table='sales_taxcollector',
        ),
        migrations.AlterModelTable(
            name='unitsale',
            table='sales_unitsale',
        ),
    ]
