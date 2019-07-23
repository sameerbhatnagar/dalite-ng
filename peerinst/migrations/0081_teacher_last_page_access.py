# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-25 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0080_auto_20190515_1401")]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="last_page_access",
            field=models.DateTimeField(
                blank=True,
                help_text="Last time the teacher went on their teacher page.",
                null=True,
            ),
        )
    ]