# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-13 14:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0084_auto_20190716_1930")]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=128)),
                ("text", models.TextField()),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MessageType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("type", models.CharField(max_length=32)),
                ("removable", models.BooleanField(default=True)),
                ("colour", models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name="SaltiseMember",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "picture",
                    models.ImageField(
                        blank=True, null=True, upload_to="images"
                    ),
                ),
            ],
        ),
        migrations.RemoveField(model_name="teacher", name="last_page_access"),
        migrations.AddField(
            model_name="teacher",
            name="last_dashboard_access",
            field=models.DateTimeField(
                blank=True,
                help_text="Last time the teacher went on their teacher dashboard.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="runningtask",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="running_tasks",
                to="peerinst.Teacher",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="peerinst.MessageType",
            ),
        ),
    ]
