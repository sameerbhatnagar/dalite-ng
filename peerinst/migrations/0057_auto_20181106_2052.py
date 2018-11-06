# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0056_auto_20181105_1442")]

    operations = [
        migrations.CreateModel(
            name="StudentNotifications",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now=True, null=True)),
                ("link", models.URLField(null=True, blank=True)),
                ("text", models.TextField()),
                ("hover_text", models.TextField(null=True, blank=True)),
            ],
        )
    ]
