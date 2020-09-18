# Generated by Django 2.2.14 on 2020-08-14 12:03

import django.core.validators
from django.db import migrations, models
import peerinst.models.group


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0103_auto_20200815_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroup',
            name='semester',
            field=models.CharField(choices=[('FALL', 'Fall'), ('SUMMER', 'Summer'), ('WINTER', 'Winter')], default=peerinst.models.group.current_semester, max_length=6),
        ),
        migrations.AlterField(
            model_name='studentgroup',
            name='year',
            field=models.PositiveIntegerField(default=peerinst.models.group.current_year, validators=[django.core.validators.MinValueValidator(2015), peerinst.models.group.max_value_current_year]),
        ),
    ]