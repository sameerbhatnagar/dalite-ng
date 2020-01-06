# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("peerinst", "0029_auto_20180324_0313"),
    ]

    operations = [
        migrations.AddField(
            model_name="blinkassignment",
            name="teacher",
            field=models.ForeignKey(
                to="peerinst.Teacher",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="blinkquestion",
            name="teacher",
            field=models.ForeignKey(
                to="peerinst.Teacher",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
    ]
