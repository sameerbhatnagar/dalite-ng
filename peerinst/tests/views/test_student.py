import json
import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)

from peerinst.models import Student, StudentGroupMembership
from peerinst.tests.generators import (
    add_groups,
    add_students,
    add_users,
    new_groups,
    new_students,
    new_users,
)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def student():
    _student = add_students(new_students(1))[0]
    _student.student.is_active = True
    _student.student.save()
    return _student


@pytest.fixture
def students():
    _students = add_students(new_students(2))
    for student in _students:
        student.student.is_active = True
        student.student.save()
    return _students


@pytest.fixture
def group():
    return add_groups(new_groups(1))[0]


def test_index_fail_on_no_logged_in_and_no_token(client):
    resp = client.get(reverse("student-page"))
    assert resp.status_code == 403
    assert any(t.name == "403.html" for t in resp.templates)
    assert (
        "You must be a logged in student to access this resource."
        in resp.content
    )


@pytest.mark.django_db
def test_index_fail_on_logged_in_not_student(client):
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
def test_index_student_logged_in(client, student):
    username, password = get_student_username_and_password(
        student.student.email
    )
    assert client.login(username=username, password=password)

    resp = client.get(reverse("student-page"))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert student.student.email in resp.content


@pytest.mark.django_db
def test_index_student_not_logged_in_token(client, student):
    token = create_student_token(
        student.student.username, student.student.email
    )

    resp = client.get(reverse("student-page") + "?token={}".format(token))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert student.student.email in resp.content


@pytest.mark.django_db
def test_index_student_logged_in_token_same_user(client, student):
    username, password = get_student_username_and_password(
        student.student.email
    )
    assert client.login(username=username, password=password)

    token = create_student_token(
        student.student.username, student.student.email
    )

    resp = client.get(reverse("student-page") + "?token={}".format(token))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert student.student.email in resp.content


@pytest.mark.django_db
def test_index_student_logged_in_token_different_user(client, students):
    username, password = get_student_username_and_password(
        students[0].student.email
    )
    assert client.login(username=username, password=password)

    token = create_student_token(
        students[1].student.username, students[1].student.email
    )

    resp = client.get(reverse("student-page") + "?token={}".format(token))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert students[1].student.email in resp.content
    assert not students[0].student.email in resp.content


@pytest.mark.django_db
def test_index_new_student(client, student):
    student.student.is_active = False
    student.student.save()

    token = create_student_token(
        student.student.username, student.student.email
    )

    assert not Student.objects.get(student=student.student).student.is_active

    resp = client.get(reverse("student-page") + "?token={}".format(token))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/index.html" for t in resp.templates)
    assert student.student.email in resp.content
    assert Student.objects.get(student=student.student).student.is_active


@pytest.mark.django_db
def test_leave_group_no_data(client):
    #  data = {"email": self.student.student.email}
    resp = client.post(reverse("student-leave-group"))
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert "Wrong data type was sent." in resp.content


@pytest.mark.django_db
def test_leave_group_wrong_data(client, student, group):
    data = {"username": student.student.username}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert "There are missing parameters." in resp.content

    data = {"group_name": group.name}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert "There are missing parameters." in resp.content

    data = {}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert "There are missing parameters." in resp.content


@pytest.mark.django_db
def test_leave_group_student_doesnt_exist(client, group):
    user = add_users(new_users(1))[0]
    data = {"username": user.username, "group_name": group.name}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert (
        "The student doesn't seem to exist. Refresh the page and try again"
        in resp.content
    )


@pytest.mark.django_db
def test_leave_group_is_member_of_group(client, student, group):
    student.groups.add(group)
    StudentGroupMembership.objects.create(student=student, group=group)

    assert group in student.groups.all()
    assert group in student.student_groups.all()
    assert StudentGroupMembership.objects.get(
        student=student, group=group
    ).current_member
    data = {"username": student.student.username, "group_name": group.name}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert group in student.groups.all()
    assert not StudentGroupMembership.objects.get(
        student=student, group=group
    ).current_member


@pytest.mark.django_db
def test_leave_group_is_not_member_of_group(client, student, group):
    data = {"username": student.student.username, "group_name": group.name}
    resp = client.post(
        reverse("student-leave-group"),
        json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert group not in student.groups.all()


def test_login_page(client):
    resp = client.get(reverse("student-login"))
    assert resp.status_code == 200
    assert any(t.name == "peerinst/student/login.html" for t in resp.templates)


@pytest.mark.django_db
def test_send_signin_link_single_account(client, student):
    data = {"email": student.student.email}
    resp = client.post(reverse("student-send-signin-link"), data)
    assert resp.status_code == 200
    assert any(
        t.name == "peerinst/student/login_confirmation.html"
        for t in resp.templates
    )
    assert "Email sent" in resp.content


@pytest.mark.django_db
def test_send_signin_link_doesnt_exist(client, student):
    data = {"email": student.student.email + "fdja"}
    resp = client.post(reverse("student-send-signin-link"), data)
    assert resp.status_code == 200
    assert any(
        t.name == "peerinst/student/login_confirmation.html"
        for t in resp.templates
    )
    assert "There was an error with your email" in resp.content


@pytest.mark.django_db
def test_send_signin_link_multiple_accounts(client, student):
    Student.objects.create(
        student=User.objects.create_user(
            username="test", email=student.student.email
        )
    )
    data = {"email": student.student.email}
    resp = client.post(reverse("student-send-signin-link"), data)
    assert resp.status_code == 200
    assert any(
        t.name == "peerinst/student/login_confirmation.html"
        for t in resp.templates
    )
    assert "Email sent" in resp.content


def test_send_signin_link_wrong_method(client):
    resp = client.get(reverse("student-send-signin-link"))
    assert resp.status_code == 405


def test_send_signin_link_missing_params(client):
    resp = client.post(reverse("student-send-signin-link"))
    assert resp.status_code == 400
    assert any(t.name == "400.html" for t in resp.templates)
    assert "There are missing parameters." in resp.content
