# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0047_auto_20180808_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroupassignment',
            name='due_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
