# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0053_auto_20181023_0341'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentGroupMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('current_member', models.BooleanField(default=True)),
                ('group', models.ForeignKey(to='peerinst.StudentGroup')),
                ('student', models.ForeignKey(to='peerinst.Student')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='student_groups',
            field=models.ManyToManyField(related_name='groups_new', through='peerinst.StudentGroupMembership', to='peerinst.StudentGroup', blank=True),
        ),
    ]
