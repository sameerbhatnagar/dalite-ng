# -*- coding: utf-8 -*-
import hashlib

import pytest
from django.core import mail

from peerinst.models import Student, StudentAssignment

from ..generators import (
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
def test_send_confirmation_email():
    student = add_students(new_students(1))[0]
    group = add_groups(new_groups(1))[0]

    err = student.send_confirmation_email(group, "localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Confirm myDALITE account"


@pytest.mark.django_db
def test_send_confirmation_email_with_localhost():
    student_ = new_students(1)
    student_[0]["email"] = "fake-email@localhost"
    student = add_students(student_)[0]
    group = add_groups(new_groups(1))[0]

    err = student.send_confirmation_email(group, "localhost")
    assert err is None

    assert not mail.outbox


@pytest.mark.django_db
def test_send_signin_email_no_group():
    student = add_students(new_students(1))[0]

    err = student.send_signin_email("localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Sign in to your myDALITE account"
    assert not any(
        line.startswith("Group: ")
        for line in mail.outbox[0]
        .message()
        .get_payload()[0]
        .as_string()
        .split("\n")
    )


@pytest.mark.django_db
def test_send_signin_email_single_group_no_assignment():
    student = add_students(new_students(1))[0]
    group = add_groups(new_groups(1))[0]
    student.groups.add(group)

    err = student.send_signin_email("localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Sign in to your myDALITE account"
    assert group.title in mail.outbox[0].message().get_payload()[0].as_string()


@pytest.mark.django_db
def test_send_signin_email_multiple_group_no_assignment():
    student = add_students(new_students(1))[0]
    groups = add_groups(new_groups(5))
    for group in groups:
        student.groups.add(group)

    err = student.send_signin_email("localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Sign in to your myDALITE account"
    for group in groups:
        assert (
            group.title
            in mail.outbox[0].message().get_payload()[0].as_string()
        )


@pytest.mark.django_db
def test_send_signin_email_single_group_single_assignment():
    student = add_students(new_students(1))[0]
    group = add_groups(new_groups(1))[0]
    student.groups.add(group)

    err = student.send_signin_email("localhost")
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[0].subject == "Sign in to your myDALITE account"
    assert group.title in mail.outbox[0].message().get_payload()[0].as_string()


@pytest.mark.django_db
def test_send_signin_email_with_localhost():
    student_ = new_students(1)
    student_[0]["email"] = "random-user@localhost"

    student = add_students(student_)[0]

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
