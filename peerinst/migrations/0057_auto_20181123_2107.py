# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0056_auto_20181122_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='ltievent',
            name='assignment_id',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='ltievent',
            name='question_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='ltievent',
            name='username',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
