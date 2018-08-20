from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.http import HttpResponseForbidden

from ..generators import add_teachers, add_users, new_teachers, new_users
from peerinst.views.decorators import teacher_required


class TestGroupAccessRequired(TestCase):
    def setUp(self):
        self.req_factory = RequestFactory()
        self.teacher_required = teacher_required(lambda req: None)


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
