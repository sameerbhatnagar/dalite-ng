from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)

from ..generators import add_students, add_users, new_students, new_users


class TestStudentPage(TestCase):
    def setUp(self):
        self.client = Client()
        self.students = add_students(new_students(2))

    def test_fail_on_no_logged_in_and_no_token(self):
        resp = self.client.get(reverse("student-page"))
        self.assertEqual(resp.status_code, 403)
        self.assertTemplateUsed(resp, "403.html")
        self.assertIn(
            "You must be a logged in student to access this resource.",
            resp.content,
        )

    def test_fail_on_logged_in_not_student(self):
        user = new_users(1)[0]
        add_users([user])
        self.assertTrue(
            self.client.login(
                username=user["username"], password=user["password"]
            )
        )

        resp = self.client.get(reverse("student-page"))
        self.assertEqual(resp.status_code, 403)
        self.assertTemplateUsed(resp, "403.html")
        self.assertIn(
            "You must be a logged in student to access this resource.",
            resp.content,
        )

    def test_student_logged_in(self):
        self.students[0].student.is_active = True
        self.students[0].student.save()
        username, password = get_student_username_and_password(
            self.students[0].student.email
        )
        self.assertTrue(
            self.client.login(username=username, password=password)
        )

        resp = self.client.get(reverse("student-page"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "peerinst/student/index.html")
        self.assertIn(self.students[0].student.email, resp.content)

    def test_student_not_logged_in_token(self):
        token = create_student_token(
            self.students[0].student.username, self.students[0].student.email
        )

        resp = self.client.get(reverse("student-page", args=(token,)))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "peerinst/student/index.html")
        self.assertIn(self.students[0].student.email, resp.content)

    def test_student_logged_in_token_same_user(self):
        self.students[0].student.is_active = True
        self.students[0].student.save()
        username, password = get_student_username_and_password(
            self.students[0].student.email
        )
        self.assertTrue(
            self.client.login(username=username, password=password)
        )

        token = create_student_token(
            self.students[0].student.username, self.students[0].student.email
        )

        resp = self.client.get(reverse("student-page", args=(token,)))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "peerinst/student/index.html")
        self.assertIn(self.students[0].student.email, resp.content)

    def test_student_logged_in_token_different_user(self):
        self.students[0].student.is_active = True
        self.students[0].student.save()
        username, password = get_student_username_and_password(
            self.students[0].student.email
        )
        self.assertTrue(
            self.client.login(username=username, password=password)
        )

        token = create_student_token(
            self.students[1].student.username, self.students[1].student.email
        )

        resp = self.client.get(reverse("student-page", args=(token,)))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "peerinst/student/index.html")
        self.assertIn(self.students[1].student.email, resp.content)
        self.assertNotIn(self.students[0].student.email, resp.content)
