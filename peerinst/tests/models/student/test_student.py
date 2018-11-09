# -*- coding: utf-8 -*-
import hashlib

import pytest
from django.core import mail
from django.core.urlresolvers import reverse

from peerinst.models import Student, StudentAssignment, StudentNotifications
from peerinst.students import create_student_token

from peerinst.tests.generators import (
    add_assignments,
    add_groups,
    add_questions,
    add_student_assignments,
    add_student_group_assignments,
    add_students,
    new_assignments,
    new_groups,
    new_questions,
    new_student_assignments,
    new_student_group_assignments,
    new_students,
)

from .fixtures import *  # noqa

MAX_USERNAME_LENGTH = 30


@pytest.mark.django_db
def test_get_or_create_new():
    data = new_students(1)[0]

    student = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert student.student.email == data["email"]
    assert student.student.username == username
    assert len(Student.objects.all()) == 1


@pytest.mark.django_db
def test_get_or_create_get():
    data = new_students(1)[0]
    add_students([data])

    student = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert student.student.email == data["email"]
    assert student.student.username == username
    assert len(Student.objects.all()) == 1


@pytest.mark.django_db
def test_send_confirmation_email(student, group):

    err = student.send_confirmation_email(group, "localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Confirm myDALITE account"


@pytest.mark.django_db
def test_send_confirmation_email_with_localhost(student, group):
    student.student.email = "fake-email@localhost"
    student.student.save()
    group = add_groups(new_groups(1))[0]

    err = student.send_confirmation_email(group, "localhost")
    assert err is None

    assert not mail.outbox


@pytest.mark.django_db
def test_send_signin_email_with_localhost(student):
    student.student.email = "fake-email@localhost"
    student.student.save()

    err = student.send_signin_email("localhost")
    assert err is None

    assert not mail.outbox


@pytest.mark.django_db
def test_send_missing_assignments():
    student = add_students(new_students(1))[0]
    group = add_groups(new_groups(1))[0]
    questions = add_questions(new_questions(10))
    assignments = add_assignments(new_assignments(2, questions))
    group_assignments = add_student_group_assignments(
        new_student_group_assignments(2, group, assignments)
    )
    add_student_assignments(
        new_student_assignments(1, group_assignments[:-1], student)
    )

    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignments[-1]
    ).exists()

    student.send_missing_assignments(group=group, host="localhost")

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignments[-1]
    ).exists()


@pytest.mark.django_db
def test_join_group(student, group):
    student.join_group(group)

    assert group in student.student_groups.all()
    assert group in student.current_groups
    assert group not in student.old_groups


@pytest.mark.django_db
def test_leave_group(student, group):
    student.join_group(group)
    student.leave_group(group)

    assert group in student.student_groups.all()
    assert group not in student.current_groups
    assert group in student.old_groups


@pytest.mark.django_db
def test_leave_group_doesnt_exist(student, group):
    student.leave_group(group)

    assert group not in student.student_groups.all()
    assert group not in student.current_groups
    assert group not in student.old_groups


@pytest.mark.django_db
def test_add_assignment(student, group_assignment):
    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment)

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotifications.objects.get(
        student=student, notification__type="new_assignment"
    ).link == reverse(
        "live",
        kwargs={
            "assignment_hash": group_assignment.hash,
            "token": create_student_token(
                student.student.username, student.student.email
            ),
        },
    )


@pytest.mark.django_db
def test_add_assignment_assignment_exists(student, group_assignment):
    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    StudentAssignment.objects.create(
        student=student, group_assignment=group_assignment
    )

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment)

    assert (
        StudentAssignment.objects.filter(
            student=student, group_assignment=group_assignment
        ).count()
        == 1
    )
    assert StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotifications.objects.get(
        student=student, notification__type="new_assignment"
    ).link == reverse(
        "live",
        kwargs={
            "assignment_hash": group_assignment.hash,
            "token": create_student_token(
                student.student.username, student.student.email
            ),
        },
    )


@pytest.mark.django_db
def test_add_assignment_with_host(student, group_assignment):

    host = "localhost"

    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment, host=host)

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert StudentNotifications.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotifications.objects.get(
        student=student, notification__type="new_assignment"
    ).link == reverse(
        "live",
        kwargs={
            "assignment_hash": group_assignment.hash,
            "token": create_student_token(
                student.student.username, student.student.email
            ),
        },
    )

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "New assignment for group {}".format(
        group_assignment.group.title
    )
