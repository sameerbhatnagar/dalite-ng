# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def copy_over_student_groups_to_field_with_through(apps, _):
    Student = apps.get_model("peerinst", "Student")
    StudentGroupMembership = apps.get_model(
        "peerinst", "StudentGroupMembership"
    )

    for student in Student.objects.all():
        for group in student.groups.all():
            StudentGroupMembership.objects.create(
                student=student, group=group, current_member=True
            )


def copy_datetime_first_to_datetime_second_old_answers(apps, _):
    Answer = apps.get_model("peerinst", "Answer")

    for answer in Answer.objects.exclude(datetime_first__isnull=True):
        if answer.datetime_start is None:
            answer.datetime_second = answer.datetime_first
            answer.datetime_first = None
            answer.save()


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0069_auto_20190221_0458")]

    operations = [
        migrations.RunPython(
            copy_datetime_first_to_datetime_second_old_answers
        )
    ]
