from peerinst.models import StudentGroupMembership


def add_to_group(students, groups):
    if not hasattr(students, "__iter__"):
        students = [students]
    if not hasattr(groups, "__iter__"):
        groups = [groups]
    for student in students:
        student.groups.add(*groups)
        for group in groups:
            StudentGroupMembership.objects.create(student=student, group=group)
