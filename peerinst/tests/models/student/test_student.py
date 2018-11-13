import hashlib

import pytest
from django.core import mail
from django.core.urlresolvers import reverse

from peerinst.models import (
    Student,
    StudentAssignment,
    StudentNotification,
    StudentGroupMembership,
)
from peerinst.students import create_student_token

from peerinst.tests.generators import add_students, new_students

from .fixtures import *  # noqa F403

MAX_USERNAME_LENGTH = 30


@pytest.mark.django_db
def test_get_or_create_new():
    data = new_students(1)[0]

    student, created = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert created
    assert student.student.email == data["email"]
    assert student.student.username == username
    assert len(Student.objects.all()) == 1


@pytest.mark.django_db
def test_get_or_create_get():
    data = new_students(1)[0]
    add_students([data])

    student, created = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert not created
    assert student.student.email == data["email"]
    assert student.student.username == username
    assert len(Student.objects.all()) == 1


@pytest.mark.django_db
def test_send_email_confirmation(student):
    err = student.send_email(mail_type="confirmation")

    assert err is None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Confirm your myDALITE account"


@pytest.mark.django_db
def test_send_email_confirmation_with_localhost(student):
    student.student.email = "fake-email@localhost"
    student.student.save()

    err = student.send_email(mail_type="confirmation")

    assert err is None
    assert not mail.outbox


@pytest.mark.django_db
def test_send_email_signin(student):
    err = student.send_email(mail_type="signin")

    assert err is None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Sign in to your myDALITE account"


@pytest.mark.django_db
def test_send_email_signin_with_localhost(student):
    student.student.email = "fake-email@localhost"
    student.student.save()
    err = student.send_email(mail_type="signin")

    assert err is None
    assert not mail.outbox


@pytest.mark.django_db
def test_send_email_new_group(student, group):
    err = student.send_email(mail_type="new_group", group=group)
    assert err is None

    assert len(mail.outbox) == 1

    assert mail.outbox[
        0
    ].subject == "You've successfully been registered to group {}".format(
        group.title
    )


@pytest.mark.django_db
def test_send_email_new_group_with_localhost(student, group):
    student.student.email = "fake-email@localhost"
    student.student.save()
    err = student.send_email(mail_type="new_group", group=group)

    assert err is None
    assert not mail.outbox


@pytest.mark.django_db
def test_send_missing_assignments(student, group_assignment):
    student.join_group(group_assignment.group)

    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()

    student.send_missing_assignments(
        group=group_assignment.group, host="localhost"
    )

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()

    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_join_group(student, group):
    student.join_group(group)

    assert group in student.student_groups.all()
    assert group in student.current_groups
    assert group not in student.old_groups


@pytest.mark.django_db
def test_leave_group(student, group):
    student.groups.add(group)
    StudentGroupMembership.objects.create(student=student, group=group)
    assert group in student.groups.all()
    assert group in student.student_groups.all()

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
    assert not StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment)

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotification.objects.get(
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
    assert not StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    StudentAssignment.objects.create(
        student=student, group_assignment=group_assignment
    )

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment)

    assert (
        StudentAssignment.objects.filter(
            student=student, group_assignment=group_assignment
        ).count()
        == 1
    )
    assert StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotification.objects.get(
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
    student.join_group(group_assignment.group)

    assert not StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert not StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()

    student.add_assignment(group_assignment, host=host)

    assert StudentAssignment.objects.filter(
        student=student, group_assignment=group_assignment
    ).exists()
    assert StudentNotification.objects.filter(
        student=student, notification__type="new_assignment"
    ).exists()
    assert StudentNotification.objects.get(
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
