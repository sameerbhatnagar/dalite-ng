# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConsent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.BooleanField()),
                ('datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=32)),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('show_order', models.PositiveIntegerField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role', models.CharField(max_length=32, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='emailtype',
            name='role',
            field=models.ForeignKey(to='tos.Role'),
        ),
        migrations.AddField(
            model_name='emailconsent',
            name='email_type',
            field=models.ForeignKey(to='tos.EmailType'),
        ),
        migrations.AddField(
            model_name='emailconsent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='emailtype',
            unique_together=set([('role', 'type')]),
        ),
    ]
