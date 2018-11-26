from django.http import HttpResponseForbidden
from django.test import RequestFactory, TestCase

from peerinst.tests.fixtures import *  # noqa
from peerinst.views.decorators import student_required, teacher_required

from ..generators import add_teachers, add_users, new_teachers, new_users


class TeacherRequired(TestCase):
    def setUp(self):
        self.req_factory = RequestFactory()
        self.teacher_required = teacher_required(lambda req: None)

    def test_teacher_required_teacher_exists(self):
        user = add_teachers(new_teachers(1))[0].user
        req = self.req_factory.get("/test")
        req.user = user

        resp = self.teacher_required(req)
        self.assertIs(resp, None)

    def test_teacher_required_not_teacher(self):
        user = add_users(new_users(1))[0]
        req = self.req_factory.get("/test")
        req.user = user

        resp = self.teacher_required(req)
        self.assertIsInstance(resp, HttpResponseForbidden)
        self.assertEqual(resp.status_code, 403)


def test_student_required__with_student(client, rf, student):
    req = rf.get("/test")
    req.user = student.student

    fct = student_required(lambda req, student: student)
    resp = fct(req)
    assert resp == student


def test_student_required__with_teacher(client, rf, teacher):
    req = rf.get("/test")
    req.user = teacher.user

    fct = student_required(lambda req, student: student)
    resp = fct(req)
    assert isinstance(resp, HttpResponseForbidden)
    assert resp.status_code == 403


def test_student_required__with_anonymous_user(client, rf, user):
    req = rf.get("/test")
    req.user = user

    fct = student_required(lambda req, student: student)
    resp = fct(req)
    assert isinstance(resp, HttpResponseForbidden)
    assert resp.status_code == 403
