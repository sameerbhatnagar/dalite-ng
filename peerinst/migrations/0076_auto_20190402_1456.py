# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-02 14:56
from __future__ import unicode_literals

from django.db import migrations, models
import peerinst.models.question


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0075_questionflag")]

    operations = [
        migrations.CreateModel(
            name="QuestionFlagReason",
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
                (
                    "title",
                    models.CharField(
                        help_text="Reason for flagging a question.",
                        max_length=100,
                        unique=True,
                        validators=[peerinst.models.question.no_hyphens],
                        verbose_name="Reason for flagging a question",
                    ),
                ),
            ],
            options={"verbose_name": "question_flag_reason"},
        ),
        migrations.AlterModelOptions(
            name="questionflag", options={"verbose_name": "flagged question"}
        ),
        migrations.AddField(
            model_name="questionflag",
            name="flag_reason",
            field=models.ManyToManyField(to="peerinst.QuestionFlagReason"),
        ),
    ]
