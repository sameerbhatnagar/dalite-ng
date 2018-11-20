# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0053_auto_20181005_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(default='PI', help_text="Choose 'peer instruction' for two-step multiple choice with rationale or 'rationale only' for a simple text response.", max_length=2, verbose_name='Question type', choices=[('PI', 'Peer instruction'), ('RO', 'Rationale only')]),
        ),
    ]
