# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0058_manual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentnotifications',
            name='link',
            field=models.URLField(max_length=500, null=True, blank=True),
        ),
    ]
