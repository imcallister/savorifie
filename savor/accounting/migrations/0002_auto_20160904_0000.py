# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='cogsassignment',
            name='unit_sale',
            field=models.ForeignKey(to='sales.UnitSale', blank=True),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations) ]
