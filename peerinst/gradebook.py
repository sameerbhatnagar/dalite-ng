import csv

from django.db.models.functions import Lower

from .models import Answer, StudentGroupMembership


class Echo:
    """
    https://docs.djangoproject.com/en/1.8/howto/outputting-csv/#streaming-large-csv-files
    An object that implements just the write method of a file-like interface
    """

    def write(self, value):
        """
        Write the value by returning it, instead of storing in buffer
        """
        return value


def group_gradebook(group):
    memberships = StudentGroupMembership.objects.filter(group=group).order_by(
        Lower("student__student__email")
    )

    # TODO handle not distributed assignments
    assignments = group.studentgroupassignment_set.all().order_by(
        "distribution_date"
    )

    answers = Answer.objects.filter(
        assignment__in=assignments.values_list("assignment", flat=True),
        user_token__in=memberships.values_list(
            "student__student__username", flat=True
        ),
    )

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    header = []
    if group.student_id_needed:
        header.append("Student ID")
    header.append("Student Email")
    for assignment in assignments:
        header.extend([q.title for q in assignment.questions])
    yield writer.writerow(header)

    for membership in memberships:
        row = []

        if group.student_id_needed:
            row.append(membership.student_school_id)

        for assignment in assignments:
            for question in assignment.questions:
                try:
                    row.append(
                        answers.get(
                            assignment=assignment.assignment,
                            question=question,
                            user_token=membership.student.student.username,
                        ).grade
                    )
                except Answer.DoesNotExist:
                    row.append("-")

        yield writer.writerow(row)
