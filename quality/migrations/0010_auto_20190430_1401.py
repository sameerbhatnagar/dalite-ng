# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-30 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("quality", "0009_auto_20190429_1859")]

    operations = [
        migrations.AlterField(
            model_name="likelihoodcache",
            name="hash",
            field=models.CharField(db_index=True, max_length=32, unique=True),
        )
    ]