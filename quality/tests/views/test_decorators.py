from django.contrib.auth.models import AnonymousUser

from peerinst.tests.fixtures import *  # noqa
from quality.views.decorators import logged_in_non_student_required


def test_logged_in_non_student_required__anonymous_user(client, rf):
    req = rf.get("/test")
    req.user = AnonymousUser()

    fct = logged_in_non_student_required(lambda req: True)
    resp = fct(req)
    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_logged_in_non_student_required__teacher(client, rf, teacher):
    req = rf.get("/test")
    req.user = teacher

    fct = logged_in_non_student_required(lambda req: True)
    resp = fct(req)
    assert resp


def test_logged_in_non_student_required__student(client, rf, student):
    req = rf.get("/test")
    req.user = student

    fct = logged_in_non_student_required(lambda req: True)
    resp = fct(req)
    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_logged_in_non_student_required__other_user(client, rf, user):
    req = rf.get("/test")
    req.user = user

    fct = logged_in_non_student_required(lambda req: True)
    resp = fct(req)
    assert resp
