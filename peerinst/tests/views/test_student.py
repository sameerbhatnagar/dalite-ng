import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)

from ..generators import add_students, add_users, new_students, new_users


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def students():
    _students = add_students(new_students(2))
    for student in _students:
        student.student.is_active = True
        student.student.save()
    return _students


def test_student_page_fail_on_no_logged_in_and_no_token(client):
    resp = client.get(reverse("student-page"))
    assert resp.status_code == 403
    assert any(t.name == "403.html" for t in resp.templates)
    assert (
        "You must be a logged in student to access this resource."
        in resp.content
    )


@pytest.mark.django_db
def test_student_page_fail_on_logged_in_not_student(client):
    user = new_users(1)[0]
    add_users([user])
    assert client.login(username=user["username"], password=user["password"])

    resp = client.get(reverse("student-page"))
    assert resp.status_code == 403
    assert any(t.name == "403.html" for t in resp.templates)
    assert (
        "You must be a logged in student to access this resource."
        in resp.content
    )


@pytest.mark.django_db
def test_student_page_student_logged_in(client, students):
    username, password = get_student_username_and_password(
        students[0].student.email
    )
    assert client.login(username=username, password=password)

    resp = client.get(reverse("student-page"))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert students[0].student.email in resp.content


@pytest.mark.django_db
def test_student_page_student_not_logged_in_token(client, students):
    token = create_student_token(
        students[0].student.username, students[0].student.email
    )

    resp = client.get(reverse("student-page", args=(token,)))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert students[0].student.email in resp.content


@pytest.mark.django_db
def test_student_page_student_logged_in_token_same_user(client, students):
    username, password = get_student_username_and_password(
        students[0].student.email
    )
    assert client.login(username=username, password=password)

    token = create_student_token(
        students[0].student.username, students[0].student.email
    )

    resp = client.get(reverse("student-page", args=(token,)))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert students[0].student.email in resp.content


@pytest.mark.django_db
def test_student_page_student_logged_in_token_different_user(client, students):
    username, password = get_student_username_and_password(
        students[0].student.email
    )
    assert client.login(username=username, password=password)

    token = create_student_token(
        students[1].student.username, students[1].student.email
    )

    resp = client.get(reverse("student-page", args=(token,)))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert students[1].student.email in resp.content
    assert not students[0].student.email in resp.content
