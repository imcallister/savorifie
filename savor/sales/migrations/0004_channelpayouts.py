# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_auto_20160916_0816'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelPayouts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payout_date', models.DateField()),
                ('channel', models.ForeignKey(to='sales.Channel')),
                ('sales', models.ManyToManyField(to='sales.Sale', blank=True)),
            ],
        ),
    ]
