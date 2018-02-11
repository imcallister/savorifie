# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2018-02-11 21:57
from __future__ import unicode_literals

import accountifie.toolkit.utils.gl_helpers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipmentline',
            name='company',
            field=models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, on_delete=django.db.models.deletion.CASCADE, to='gl.Company'),
        ),
    ]
