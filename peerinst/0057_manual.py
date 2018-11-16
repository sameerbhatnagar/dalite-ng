# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0056_auto_20181106_2052")]

    operations = [
        migrations.CreateModel(
            name="StudentNotificationType",
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
                ("type", models.CharField(unique=True, max_length=32)),
                ("icon", models.TextField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="studentgroupmembership",
            unique_together=set([("student", "group")]),
        ),
        migrations.AddField(
            model_name="studentnotifications",
            name="notification",
            field=models.ForeignKey(to="peerinst.StudentNotificationType"),
        ),
        migrations.AddField(
            model_name="studentnotifications",
            name="student",
            field=models.ForeignKey(to="peerinst.Student"),
        ),
    ]
