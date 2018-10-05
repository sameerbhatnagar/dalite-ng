# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0052_auto_20180924_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='RationaleOnlyQuestion',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('peerinst.question',),
        ),
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(default='PI', max_length=2, choices=[('PI', 'PeerInst'), ('RO', 'RationaleOnly')]),
        ),
    ]
