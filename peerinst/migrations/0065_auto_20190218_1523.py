from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0064_auto_20190218_1521")]

    operations = [
        migrations.AddField(
            model_name="answer",
            name="datetime_first",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="answer",
            name="datetime_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
