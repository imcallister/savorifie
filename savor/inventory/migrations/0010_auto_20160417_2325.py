# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_auto_20160417_2242'),
    ]

    operations = [
        migrations.CreateModel(
            name='FulfillUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_date', models.DateField()),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
                ('status', models.CharField(max_length=30, choices=[(b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')])),
            ],
            options={
                'db_table': 'inventory_fulfillupdate',
            },
        ),
        migrations.RemoveField(
            model_name='fulfillment',
            name='status',
        ),
        migrations.AddField(
            model_name='fulfillupdate',
            name='fulfillment',
            field=models.ForeignKey(to='inventory.Fulfillment'),
        ),
    ]
