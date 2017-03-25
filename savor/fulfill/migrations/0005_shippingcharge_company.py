# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import accountifie.toolkit.utils.gl_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('gl', '0002_transaction_bmo_id'),
        ('fulfill', '0004_auto_20161001_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingcharge',
            name='company',
            field=models.ForeignKey(default=accountifie.toolkit.utils.gl_helpers.get_default_company, to='gl.Company'),
        ),
    ]
