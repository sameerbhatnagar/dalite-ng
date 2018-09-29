# -*- coding: utf-8 -*-
import hashlib
import pytest
from peerinst.models import Student, StudentAssignment
from ..generators import (
    add_assignments,
    add_groups,
    add_students,
    add_questions,
    add_student_assignments,
    add_student_group_assignments,
    new_assignments,
    new_groups,
    new_students,
    new_questions,
    new_student_assignments,
    new_student_group_assignments,
)

MAX_USERNAME_LENGTH = 30


@pytest.mark.django_db
def test_new_student():
    data = new_students(1)[0]

    student = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert student.student.email == data["email"]
    assert student.student.username == username


@pytest.mark.django_db
def test_get_student():
    data = new_students(1)[0]
    add_students([data])

    student = Student.get_or_create(**data)
    username = hashlib.md5(data["email"].encode()).hexdigest()[
        :MAX_USERNAME_LENGTH
    ]

    assert isinstance(student, Student)
    assert student.student.email == data["email"]
    assert student.student.username == username


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
