# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0059_auto_20181108_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now=True, null=True)),
                ('link', models.URLField(max_length=500, null=True, blank=True)),
                ('text', models.TextField()),
                ('hover_text', models.TextField(null=True, blank=True)),
                ('notification', models.ForeignKey(to='peerinst.StudentNotificationType')),
            ],
        ),
        migrations.RemoveField(
            model_name='studentnotifications',
            name='notification',
        ),
        migrations.RemoveField(
            model_name='studentnotifications',
            name='student',
        ),
        migrations.RenameField(
            model_name='studentgroupmembership',
            old_name='sending_email',
            new_name='send_email',
        ),
        migrations.AddField(
            model_name='student',
            name='send_reminder_email_day_before',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='student',
            name='send_reminder_email_every_day',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentassignment',
            name='reminder_sent',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='studentgroupassignment',
            name='reminder_days',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.DeleteModel(
            name='StudentNotifications',
        ),
        migrations.AddField(
            model_name='studentnotification',
            name='student',
            field=models.ForeignKey(to='peerinst.Student'),
        ),
    ]
