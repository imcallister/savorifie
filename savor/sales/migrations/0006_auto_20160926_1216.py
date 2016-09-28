# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_channelpayouts_payout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salestax',
            name='sale',
            field=models.ForeignKey(related_name='sales_tax', to='sales.Sale'),
        ),
    ]
