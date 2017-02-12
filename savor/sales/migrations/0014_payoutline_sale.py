# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-02-01 14:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0013_auto_20170201_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='payoutline',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payoutline_sale', to='sales.Sale'),
        ),
    ]