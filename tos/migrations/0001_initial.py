# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Consent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.BooleanField()),
                ('datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='Tos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.PositiveIntegerField()),
                ('hash', models.CharField(max_length=32, editable=False)),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('current', models.BooleanField()),
                ('role', models.ForeignKey(to='tos.Role')),
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
        migrations.AddField(
            model_name='consent',
            name='tos',
            field=models.ForeignKey(to='tos.Tos'),
        ),
        migrations.AddField(
            model_name='consent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tos',
            unique_together=set([('role', 'hash'), ('role', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailtype',
            unique_together=set([('role', 'type')]),
        ),
    ]
