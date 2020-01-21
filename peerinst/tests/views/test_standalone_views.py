import pytest

from peerinst.tests.generators import (
    add_groups,
    add_students,
    add_teachers,
    new_groups,
    new_students,
    new_teachers,
)


@pytest.fixture
def group():
    return add_groups(new_groups(1))[0]


@pytest.fixture
def student():
    _student = add_students(new_students(1))[0]
    _student.student.is_active = True
    _student.student.save()
    return _student


@pytest.fixture
def students():
    _students = add_students(new_students(2))
    for _student in _students:
        _student.student.is_active = True
        _student.student.save()
    return _students


@pytest.fixture
def teacher():
    _teacher = add_teachers(new_teachers(1))[0]
    _teacher.user.is_active = True
    _teacher.user.save()
    return _teacher


def test_signup_through_link(client, group, student):
    pass


def test_signup_through_link_logged_in(client, group, student):
    pass


def test_signup_through_link_logged_in_other_student(client, group, students):
    pass


def test_signup_through_link_logged_in_other_teacher(
    client, group, student, teacher
):
    pass


def test_signup_through_link_invalid_hash(client):
    pass


def test_signup_through_link_not_post(client, group):
    pass


def test_signup_through_link_invalid_form(client, group):
    pass


def test_signup_through_link_student_doesnt_exist(client, group):
    pass


def test_confirm_signup_through_link(client, group, student):
    pass


def test_confirm_signup_through_link_logged_in(client, group, student):
    pass


def test_confirm_signup_through_link_logged_in_other_student(
    client, group, students
):
    pass


def test_confirm_signup_through_link_logged_in_teacher(
    client, group, student, teacher
):
    pass


def test_confirm_signup_through_link_group_doesnt_exist(client):
    pass


def test_confirm_signup_through_link_student_doesnt_exist(
    client, group, student
):
    pass
