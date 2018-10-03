# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_over_student_groups_to_field_with_through(apps, schema_editor):
    Student = apps.get_model("peerinst", "Student")
    StudentGroupMembership = apps.get_model(
        "peerinst", "StudentGroupMembership"
    )

    for student in Student.objects.all():
        for group in student.groups.all():
            StudentGroupMembership.objects.create(
                student=student, group=group, current_member=True
            )


class Migration(migrations.Migration):

    dependencies = [("peerinst", "0053_auto_20181003_1438")]

    operations = [
        migrations.RunPython(copy_over_student_groups_to_field_with_through)
    ]
