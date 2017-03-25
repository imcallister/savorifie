# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0035_auto_20160705_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='fulfillment',
            name='status',
            field=models.CharField(default='completed', max_length=20, choices=[(b'requested', b'requested'), (b'partial', b'partial'), (b'completed', b'completed')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fulfillline',
            name='fulfillment',
            field=models.ForeignKey(related_name='fulfill_lines', to='inventory.Fulfillment'),
        ),
        migrations.AlterField(
            model_name='fulfillupdate',
            name='fulfillment',
            field=models.ForeignKey(related_name='fulfill_updates', to='inventory.Fulfillment'),
        ),
        migrations.AlterField(
            model_name='skuunit',
            name='sku',
            field=models.ForeignKey(related_name='skuunit', blank=True, to='inventory.Product', null=True),
        ),
    ]
