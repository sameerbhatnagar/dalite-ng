from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from peerinst.models import Student
from ..generators import add_students, new_students


class TestStudentLoginPage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_login_page(self):
        resp = self.client.get(reverse("student-login"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/student_login.html")


class TestStudentSendSigninLink(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = add_students(new_students(1))[0]

    def test_student_send_signin_link_single_account(self):
        data = {"email": self.student.student.email}
        resp = self.client.post(reverse("student-send-signin-link"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "registration/student_login_confirmation.html"
        )
        self.assertIn("Email sent", resp.content)

    def test_student_send_signin_link_doesnt_exist(self):
        data = {"email": self.student.student.email + "fdja"}
        resp = self.client.post(reverse("student-send-signin-link"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "registration/student_login_confirmation.html"
        )
        self.assertIn("There was an error with your email", resp.content)

    def test_student_send_signin_link_multiple_accounts(self):
        Student.objects.create(
            student=User.objects.create_user(
                username="test", email=self.student.student.email
            )
        )
        data = {"email": self.student.student.email}
        resp = self.client.post(reverse("student-send-signin-link"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            resp, "registration/student_login_confirmation.html"
        )
        self.assertIn("Email sent", resp.content)

    def test_student_send_signin_link_wrong_method(self):
        resp = self.client.get(reverse("student-send-signin-link"))
        self.assertEqual(resp.status_code, 405)

    def test_student_send_signin_link_missing_params(self):
        resp = self.client.post(reverse("student-send-signin-link"))
        self.assertEqual(resp.status_code, 400)
        self.assertTemplateUsed(resp, "400.html")
        self.assertIn("There are missing parameters.", resp.content)
