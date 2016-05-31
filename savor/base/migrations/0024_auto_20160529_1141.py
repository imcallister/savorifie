# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_auto_20160529_1011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditcardtrans',
            name='expense_account',
        ),
        migrations.RemoveField(
            model_name='historicalcreditcardtrans',
            name='expense_account',
        ),
    ]
