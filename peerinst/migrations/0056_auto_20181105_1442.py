# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0055_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verifieddomain',
            options={},
        ),
        migrations.AddField(
            model_name='studentgroupmembership',
            name='sending_email',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='identifier',
            field=models.CharField(help_text='A unique identifier for this assignment used for inclusion in a course.', max_length=100, serialize=False, verbose_name='identifier', primary_key=True),
        ),
        migrations.AlterField(
            model_name='verifieddomain',
            name='domain',
            field=models.CharField(help_text='Teacher-only email domain, if available. Email addresses with these domains will be treated as verified.', max_length=100),
        ),
    ]
