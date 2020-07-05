# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0045_studentgroupassignment_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroupassignment',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
