# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peerinst', '0060_auto_20181112_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentgroupmembership',
            old_name='send_email',
            new_name='send_emails',
        ),
    ]
