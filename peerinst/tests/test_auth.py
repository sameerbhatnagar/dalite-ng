from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase, override_settings

from peerinst.auth import authenticate_student
from peerinst.models import Student, Teacher
from peerinst.students import (
    get_old_lti_student_username_and_password,
    get_student_username_and_password,
)


class TestAuthenticateStudent(TestCase):
    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_user_doesnt_exist(self):
        test = {"email": "test@localhost"}

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertFalse(is_lti)
        self.assertTrue(User.objects.filter(email=test["email"]).exists())
        self.assertTrue(
            Student.objects.filter(student__email=test["email"]).exists()
        )

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_standalone_student_exists(self):
        test = {"email": "test@localhost"}
        username, password = get_student_username_and_password(**test)
        Student.objects.create(
            student=User.objects.create_user(
                username=username, email=test["email"], password=password
            )
        )

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_standalone_user_exists(self):
        test = {"email": "test@localhost"}
        username, password = get_student_username_and_password(**test)
        User.objects.create_user(
            username=username, email=test["email"], password=password
        )

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertFalse(is_lti)
        self.assertTrue(
            Student.objects.filter(student__email=test["email"]).exists()
        )

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_lti_student_exists(self):
        test = {"email": "test@localhost"}
        user_id = test["email"][:-10]
        username, password = get_old_lti_student_username_and_password(user_id)
        Student.objects.create(
            student=User.objects.create_user(
                username=username, email=test["email"], password=password
            )
        )
        new_username, _ = get_student_username_and_password(test["email"])

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertTrue(is_lti)
        self.assertEqual(len(User.objects.filter(email=test["email"])), 1)
        self.assertEqual(
            len(Student.objects.filter(student__email=test["email"])), 1
        )
        self.assertFalse(User.objects.filter(username=new_username).exists())
        self.assertFalse(
            Student.objects.filter(student__username=new_username).exists()
        )

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_lti_user_exists(self):
        test = {"email": "test@localhost"}
        user_id = test["email"][:-10]
        username, password = get_old_lti_student_username_and_password(user_id)
        User.objects.create_user(
            username=username, email=test["email"], password=password
        )
        new_username, _ = get_student_username_and_password(test["email"])

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertTrue(is_lti)
        self.assertEqual(len(User.objects.filter(email=test["email"])), 1)
        self.assertTrue(
            Student.objects.filter(student__email=test["email"]).exists()
        )
        self.assertEqual(
            len(Student.objects.filter(student__email=test["email"])), 1
        )
        self.assertFalse(User.objects.filter(username=new_username).exists())
        self.assertFalse(
            Student.objects.filter(student__username=new_username).exists()
        )

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_standalone_user_exists_is_teacher(self):
        test = {"email": "test@localhost"}
        username, password = get_student_username_and_password(**test)
        Teacher.objects.create(
            user=User.objects.create_user(
                username=username, email=test["email"], password=password
            )
        )

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertFalse(is_lti)
        self.assertFalse(
            Student.objects.filter(student__email=test["email"]).exists()
        )

    @override_settings(PASSWORD_GENERATOR_NONCE="key")
    def test_lti_user_exists_is_teacher(self):
        test = {"email": "test@localhost"}
        user_id = test["email"][:-10]
        username, password = get_old_lti_student_username_and_password(user_id)
        Teacher.objects.create(
            user=User.objects.create_user(
                username=username, email=test["email"], password=password
            )
        )

        user, is_lti = authenticate_student(HttpRequest(), **test)
        self.assertIsInstance(user, User)
        self.assertTrue(is_lti)
        self.assertFalse(
            Student.objects.filter(student__email=test["email"]).exists()
        )
