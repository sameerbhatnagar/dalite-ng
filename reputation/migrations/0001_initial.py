# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-14 14:35


import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NAnswersCriterion",
            fields=[
                (
                    "version",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "name",
                    models.CharField(
                        default="n_answers", editable=False, max_length=32
                    ),
                ),
                (
                    "floor",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Any number of answers up to and including this evaluates to 0.",
                        verbose_name="Number floor",
                    ),
                ),
                (
                    "ceiling",
                    models.PositiveIntegerField(
                        default=100,
                        help_text="Any number of answers from and including this evaluates to 1. If set to 0, no ceiling is set.",
                        verbose_name="Number ceiling",
                    ),
                ),
                (
                    "growth_rate",
                    models.FloatField(
                        default=0.01,
                        help_text="Steepness of the slope.",
                        validators=[
                            django.core.validators.MinValueValidator(0.0)
                        ],
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Reputation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
        ),
        migrations.CreateModel(
            name="ReputationType",
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
                ("type", models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="UsesCriterion",
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
                ("name", models.CharField(max_length=32)),
                ("version", models.PositiveIntegerField()),
                ("weight", models.PositiveIntegerField()),
                (
                    "reputation_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criterions",
                        to="reputation.ReputationType",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="reputation",
            name="reputation_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="reputation.ReputationType",
            ),
        ),
        migrations.AddField(
            model_name="nanswerscriterion",
            name="for_reputation_types",
            field=models.ManyToManyField(to="reputation.ReputationType"),
        ),
    ]