# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0001_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashflow',
            name='company',
            field=models.ForeignKey(default=b'SAV', to='gl.Company'),
        ),
        migrations.AddField(
            model_name='historicalcashflow',
            name='company',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='gl.Company', null=True),
        ),
    ]
