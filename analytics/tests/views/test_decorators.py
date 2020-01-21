from django.contrib.auth.models import AnonymousUser

from analytics.views.decorators import staff_required
from peerinst.tests.fixtures import *  # noqa


def test_logged_in_non_student_required__anonymous_user(client, rf):
    req = rf.get("/test")
    req.user = AnonymousUser()

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_logged_in_non_student_required__teacher(client, rf, teacher):
    req = rf.get("/test")
    req.user = teacher.user

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp


def test_logged_in_non_student_required__teacher__staff(client, rf, teacher):
    req = rf.get("/test")
    teacher.user.is_staff = True
    teacher.user.save()
    req.user = teacher.user

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp


def test_logged_in_non_student_required__student(client, rf, student):
    req = rf.get("/test")
    req.user = student.student

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_logged_in_non_student_required__other_user(client, rf, user):
    req = rf.get("/test")
    req.user = user

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp


def test_logged_in_non_student_required__other_user__staff(client, rf, staff):
    req = rf.get("/test")
    req.user = staff

    fct = staff_required(lambda req: True)
    resp = fct(req)
    assert resp
