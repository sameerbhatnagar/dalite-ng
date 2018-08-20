from django.test import TestCase
from django.contrib.auth.models import User
from peerinst.auth import authenticate_student
from peerinst.models import Student
from peerinst.students import (
    get_student_username_and_password,
    get_old_lti_student_username_and_password,
)


class TestAuthenticateStudent(TestCase):
    def test_user_doesnt_exist(self):
        test = {"email": "test@localhost"}

        err = authenticate_student(**test)
        self.assertIs(err, None)
        self.assertTrue(User.objects.filter(email=test["email"]).exists())
        self.assertTrue(
            Student.objects.filter(student__email=test["email"]).exists()
        )

    def test_standalone_student_exists(self):
        test = {"email": "test@localhost"}
        username, password = get_student_username_and_password(**test)
        Student.objects.create(
            student=User.objects.create_user(
                username=username, email=test["email"], password=password
            )
        )

        err = authenticate_student(**test)
        self.assertIs(err, None)

    def test_standalone_user_exists(self):
        test = {"email": "test@localhost"}
        username, password = get_student_username_and_password(**test)
        User.objects.create_user(
            username=username, email=test["email"], password=password
        )

        err = authenticate_student(**test)
        self.assertIs(err, None)
        self.assertTrue(
            Student.objects.filter(student__email=test["email"]).exists()
        )

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

        err = authenticate_student(**test)
        self.assertIs(err, None)
        self.assertEqual(len(User.objects.filter(email=test["email"])), 1)
        self.assertEqual(
            len(Student.objects.filter(student__email=test["email"])), 1
        )
        self.assertFalse(User.objects.filter(username=new_username).exists())
        self.assertFalse(
            Student.objects.filter(student__username=new_username).exists()
        )

    def test_lti_user_exists(self):
        test = {"email": "test@localhost"}
        user_id = test["email"][:-10]
        username, password = get_old_lti_student_username_and_password(user_id)
        User.objects.create_user(
            username=username, email=test["email"], password=password
        )
        new_username, _ = get_student_username_and_password(test["email"])

        err = authenticate_student(**test)
        self.assertIs(err, None)
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
