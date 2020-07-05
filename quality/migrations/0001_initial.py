# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-23 20:39


from django.db import migrations, models
import django.db.models.deletion
import dalite.models.custom_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MinCharsCriterion",
            fields=[
                (
                    "version",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "uses_rules",
                    models.TextField(
                        blank=True,
                        help_text="Comma separated list of used rules for the criterion found as the fields of the associated rules object. Make sure to use the verbose_name",
                    ),
                ),
                ("is_beta", models.BooleanField(default=False)),
                (
                    "name",
                    models.CharField(
                        default="min_chars", editable=False, max_length=32
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="MinCharsCriterionRules",
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
                    "threshold",
                    dalite.models.custom_fields.ProbabilityField(
                        help_text="Minimum value for the answer to be accepted",
                        verbose_name="Threshold",
                    ),
                ),
                (
                    "min_chars",
                    models.PositiveIntegerField(
                        help_text="The minimum number of characters needed by a rationale.",
                        verbose_name="Min characters",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="MinWordsCriterion",
            fields=[
                (
                    "version",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "uses_rules",
                    models.TextField(
                        blank=True,
                        help_text="Comma separated list of used rules for the criterion found as the fields of the associated rules object. Make sure to use the verbose_name",
                    ),
                ),
                ("is_beta", models.BooleanField(default=False)),
                (
                    "name",
                    models.CharField(
                        default="min_words", editable=False, max_length=32
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="MinWordsCriterionRules",
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
                    "threshold",
                    dalite.models.custom_fields.ProbabilityField(
                        help_text="Minimum value for the answer to be accepted",
                        verbose_name="Threshold",
                    ),
                ),
                (
                    "min_words",
                    models.PositiveIntegerField(
                        help_text="The minimum number of words needed by a rationale.",
                        verbose_name="Min words",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="NegWordsCriterion",
            fields=[
                (
                    "version",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "uses_rules",
                    models.TextField(
                        blank=True,
                        help_text="Comma separated list of used rules for the criterion found as the fields of the associated rules object. Make sure to use the verbose_name",
                    ),
                ),
                ("is_beta", models.BooleanField(default=False)),
                (
                    "name",
                    models.CharField(
                        default="neg_words", editable=False, max_length=32
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="NegWordsCriterionRules",
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
                    "threshold",
                    dalite.models.custom_fields.ProbabilityField(
                        help_text="Minimum value for the answer to be accepted",
                        verbose_name="Threshold",
                    ),
                ),
                (
                    "neg_words",
                    dalite.models.custom_fields.CommaSepField(
                        blank=True,
                        help_text="Words considered to be negative.",
                        null=True,
                        verbose_name="Negative words",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Quality",
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
            name="QualityType",
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
            ],
        ),
        migrations.CreateModel(
            name="QualityUseType",
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
            ],
        ),
        migrations.CreateModel(
            name="RejectedAnswer",
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
                ("rationale", models.TextField()),
                (
                    "reasons",
                    models.TextField(
                        help_text="json string containing info about criterions used to reject the rationale"
                    ),
                ),
                (
                    "quality",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="quality.Quality",
                    ),
                ),
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
                ("rules", models.PositiveIntegerField()),
                ("weight", models.PositiveIntegerField()),
                (
                    "quality",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criterions",
                        to="quality.Quality",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="quality",
            name="quality_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="quality.QualityType",
            ),
        ),
        migrations.AddField(
            model_name="quality",
            name="quality_use_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="quality.QualityUseType",
            ),
        ),
        migrations.AddField(
            model_name="negwordscriterion",
            name="for_quality_types",
            field=models.ManyToManyField(to="quality.QualityType"),
        ),
        migrations.AddField(
            model_name="minwordscriterion",
            name="for_quality_types",
            field=models.ManyToManyField(to="quality.QualityType"),
        ),
        migrations.AddField(
            model_name="mincharscriterion",
            name="for_quality_types",
            field=models.ManyToManyField(to="quality.QualityType"),
        ),
    ]
