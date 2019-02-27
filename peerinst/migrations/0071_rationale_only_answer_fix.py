# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def change_answers_with_index_0_to_1(apps, _):
    Answer = apps.get_model("peerinst", "Answer")
    for answer in Answer.objects.filter(first_answer_choice=0):
        answer.first_answer_choice = 1
        answer.save()


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0070_answer_datetime_fix")]

    operations = [migrations.RunPython(change_answers_with_index_0_to_1)]
