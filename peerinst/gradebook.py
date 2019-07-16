# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.db.models.functions import Lower

from .models import (
    Answer,
    StudentAssignment,
    StudentGroup,
    StudentGroupAssignment,
    StudentGroupMembership,
)


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
    """
    Parameters
    ----------
    StudentGroup Hash

    Returns:
    --------
    csv writer object with aggregate results for each student
    across all assignments
    """

    memberships = StudentGroupMembership.objects.filter(group=group).order_by(
        Lower("student__student__email")
    )

    assignments = group.studentgroupassignment_set.filter(
        distribution_date__isnull=False
    ).order_by("distribution_date")

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    header = []
    if group.student_id_needed:
        header.append("Student ID")
    header.append("Student Email")
    for assignment in assignments:
        header.extend(
            [
                "{} - {}".format(quantity, assignment.assignment.identifier)
                for quantity in ["n_correct", "n_completed"]
            ]
        )
    yield writer.writerow(header)

    for membership in memberships:
        row = []

        if group.student_id_needed:
            row.append(membership.student_school_id)

        row.append(membership.student.student.email)

        for assignment in assignments:
            try:
                row.append(
                    assignment.studentassignment_set.get(
                        student=membership.student
                    ).results["n_correct"]
                )
                row.append(
                    assignment.studentassignment_set.get(
                        student=membership.student
                    ).results["n_completed"]
                )
            except StudentAssignment.DoesNotExist:
                row.append("-")
                row.append("-")
        yield writer.writerow(row)


def groupassignment_gradebook(group, assignment):
    """
    Parameters
    ----------
    StudentGroup Hash
    StudentGroupAssignment hash

    Returns:
    -------
    csv writer object with results for each student in this assignment
    for each question

    """

    memberships = StudentGroupMembership.objects.filter(group=group).order_by(
        Lower("student__student__email")
    )

    answers = Answer.objects.filter(
        assignment=assignment.assignment,
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
    header.extend([q.title for q in assignment.questions])
    yield writer.writerow(header)

    for membership in memberships:
        row = []

        if group.student_id_needed:
            row.append(membership.student_school_id)

        row.append(membership.student.student.email)

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


def compute_gradebook(group_pk, assignment_pk=None):
    """
    Computes the gradebook for the given group and assignment (if not None).

    Parameters
    ----------
    group_pk : int
        Primary key of the group for which to compute the gradebook
    assignment_pk : Optional[int] (default : None)
        Primary key of the assignment for which to compute the gradebook

    Returns
    -------
    Either
        If group gradebook wanted
            {
                assignments: List[str]
                    Assignment identifier
                school_id_needed: bool
                    If a school id is needed
                results: [{
                    school_id: Optional[str]
                        School id if needed
                    email: str
                        Student email
                    assignments: [{
                        n_completed: int
                            Number of completed questions
                        n_correct: int
                            Number of correct questions
                    }]
                }]
            }
        If assignment gradebook wanted
            {
                questions: List[str]
                    Question title
                school_id_needed: bool
                    If a school id is needed
                results: [{
                    school_id: Optional[str]
                        School id if needed
                    email: str
                        Student email
                    questions: List[float]
                        Grade for each question
                }]
            }

    Raises
    ------
    StudentGroup.DoesNotExist
        When the group pk doesn't correspond to an existing group
    StudentGroupAssignment.DoesNotExist
        When the assignment pk doesn't correspond to an existing group
    """
    group = StudentGroup.objects.get(pk=group_pk)

    if assignment_pk is not None:
        assignment = StudentGroupAssignment.objects.get(pk=assignment_pk)
    else:
        assignment = None

    memberships = StudentGroupMembership.objects.filter(group=group).order_by(
        Lower("student__student__email")
    )

    if assignment is None:
        assignments = group.studentgroupassignment_set.filter(
            distribution_date__isnull=False
        ).order_by("distribution_date")
        results = {
            "assignments": [
                _assignment.assignment.identifier
                for _assignment in assignments
            ],
            "school_id_needed": group.student_id_needed,
            "results": [
                {
                    "school_id": membership.student_school_id
                    if group.student_id_needed
                    else None,
                    "email": membership.student.student.email,
                    "assignments": [
                        {
                            key: val
                            for key, val in assignment.studentassignment_set.get(  # noqa
                                student=membership.student
                            ).results.items()
                            if key in ("n_completed", "n_correct")
                        }
                        if assignment.studentassignment_set.filter(
                            student=membership.student
                        ).exists()
                        else None
                        for _assignment in assignments
                    ],
                }
                for membership in memberships
            ],
        }

    else:
        answers = Answer.objects.filter(assignment=assignment.assignment)
        questions = assignment.questions
        results = {
            "questions": [question.title for question in questions],
            "school_id_needed": group.student_id_needed,
            "results": [
                {
                    "school_id": membership.student_school_id
                    if group.student_id_needed
                    else None,
                    "email": membership.student.student.email,
                    "questions": [
                        answers.get(
                            question=question,
                            user_token=membership.student.student.username,
                        ).grade
                        if answers.filter(
                            question=question,
                            user_token=membership.student.student.username,
                        ).exists()
                        else None
                        for question in questions
                    ],
                }
                for membership in memberships
            ],
        }
    return results
