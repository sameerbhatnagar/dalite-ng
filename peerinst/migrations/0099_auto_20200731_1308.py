# Generated by Django 2.2.14 on 2020-07-31 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0098_auto_20200730_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
    ]