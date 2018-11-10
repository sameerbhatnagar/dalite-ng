from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.keys import Keys
import time
import unittest

from django.contrib.auth.models import Permission, Group
from peerinst.models import User, Question, Assignment
from tos.models import Role, Tos


def ready_user(pk):
    user = User.objects.get(pk=pk)
    user.text_pwd = user.password
    user.password = make_password(user.text_pwd)
    user.save()
    return user


class NewUserTests(StaticLiveServerTestCase):
    fixtures = ["test_users.yaml"]

    def setUp(self):
        try:
            self.browser = webdriver.Chrome()
        except SessionNotCreatedException:
            self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)

        self.validated_teacher = ready_user(1)
        self.inactive_user = ready_user(3)

        self.group = Group.objects.get(name="Teacher")
        self.assertFalse(self.group.permissions.all())

        permission = Permission.objects.get(codename="add_question")
        self.group.permissions.add(permission)
        permission = Permission.objects.get(codename="change_question")
        self.group.permissions.add(permission)
        self.assertEqual(self.group.permissions.count(), 2)

        self.assertFalse(self.validated_teacher.get_all_permissions())

        # Add TOS for teachers
        role = Role.objects.get(role="teacher")
        new_TOS = Tos(version=1, text="Test", current=True, role=role)
        new_TOS.save()

    def tearDown(self):
        self.browser.quit()
        os.remove(os.path.join(os.path.dirname(__file__), "geckodriver.log"))

    def test_new_user(self):
        # Hit landing page
        self.browser.get(self.live_server_url + "/#Features")
        self.assertIn(
            "Features", self.browser.find_element_by_tag_name("h1").text
        )
        self.assertIn(
            "Login",
            self.browser.find_element_by_id("link-to-login-or-welcome").text,
        )
        self.browser.find_element_by_link_text("Signup").click()

        # Sign up page rendered
        self.assertIn(
            "Sign Up", self.browser.find_element_by_tag_name("h1").text
        )

        # New user can sign up
        form = self.browser.find_element_by_tag_name("form")
        self.assertEqual(form.get_attribute("method"), "post")

        inputbox = self.browser.find_element_by_id("id_email")
        inputbox.send_keys("test@test.com")

        inputbox = self.browser.find_element_by_id("id_username")
        inputbox.send_keys("test")

        inputbox = self.browser.find_element_by_id("id_password1")
        inputbox.send_keys("jka+sldfa+soih")

        inputbox = self.browser.find_element_by_id("id_password2")
        inputbox.send_keys("jka+sldfa+soih")

        inputbox = self.browser.find_element_by_id("id_url")
        inputbox.clear()
        inputbox.send_keys("http://www.mydalite.org")

        inputbox.submit()

        # New user redirected post sign up
        self.assertIn(
            "Processing Request",
            self.browser.find_element_by_tag_name("h1").text,
        )

        # New user cannot sign in
        self.browser.get(self.live_server_url + "/login")
        inputbox = self.browser.find_element_by_id("id_username")
        inputbox.send_keys("test")

        inputbox = self.browser.find_element_by_id("id_password")
        inputbox.send_keys("jka+sldfa+soih")

        inputbox.submit()

        # Small pause to see last page
        time.sleep(1)

        assert (
            "your account has not yet been activated"
            in self.browser.page_source
        )

    def test_new_user_with_email_server_error(self):

        with self.settings(EMAIL_BACKEND=""):
            self.browser.get(self.live_server_url + "/signup")

            form = self.browser.find_element_by_tag_name("form")
            self.assertEqual(form.get_attribute("method"), "post")

            inputbox = self.browser.find_element_by_id("id_email")
            inputbox.send_keys("test@test.com")

            inputbox = self.browser.find_element_by_id("id_username")
            inputbox.send_keys("test")

            inputbox = self.browser.find_element_by_id("id_password1")
            inputbox.send_keys("jka+sldfa+soih")

            inputbox = self.browser.find_element_by_id("id_password2")
            inputbox.send_keys("jka+sldfa+soih")

            inputbox = self.browser.find_element_by_id("id_url")
            inputbox.clear()
            inputbox.send_keys("http://www.mydalite.org")

            inputbox.submit()

            time.sleep(1)

            assert "500" in self.browser.page_source

    def test_inactive_user_login(self):
        self.browser.get(self.live_server_url + "/login")

        # Inactive user cannot login
        inputbox = self.browser.find_element_by_id("id_username")
        inputbox.send_keys(self.inactive_user.username)

        inputbox = self.browser.find_element_by_id("id_password")
        inputbox.send_keys(self.inactive_user.text_pwd)

        inputbox.submit()

        time.sleep(1)

        assert (
            "your account has not yet been activated"
            in self.browser.page_source
        )

    def __test_validated_user(self):
        # Validated user can login
        self.browser.get(self.live_server_url + "/login")

        # Validated user can browse certain pages

        # Validated user cannot access account

        # Validated user can logout

    def test_teacher(self):
        # Teacher can login and access account
        self.browser.get(self.live_server_url + "/login")
        inputbox = self.browser.find_element_by_id("id_username")
        inputbox.send_keys(self.validated_teacher.username)

        inputbox = self.browser.find_element_by_id("id_password")
        inputbox.send_keys(self.validated_teacher.text_pwd)

        inputbox.submit()

        time.sleep(1)

        assert "Terms of Service" in self.browser.page_source

        button = self.browser.find_element_by_id("tos-accept")
        button.click()

        assert "My Account" in self.browser.page_source
        assert "Terms of service: Sharing" in self.browser.page_source

        # Welcome authenticated user on landing pages
        self.browser.get(self.live_server_url)
        welcome = self.browser.find_element_by_id("link-to-login-or-welcome")
        assert (
            "Welcome back " + self.validated_teacher.username in welcome.text
        )

        # Logout and log back in -> skip tos
        self.browser.get(self.live_server_url + "/logout")
        self.browser.get(self.live_server_url + "/login")
        inputbox = self.browser.find_element_by_id("id_username")
        inputbox.send_keys(self.validated_teacher.username)

        inputbox = self.browser.find_element_by_id("id_password")
        inputbox.send_keys(self.validated_teacher.text_pwd)

        inputbox.submit()

        time.sleep(1)
        assert "My Account" in self.browser.page_source

        # Add a new current TOS for teachers and refresh account -> tos
        role = Role.objects.get(role="teacher")
        new_TOS = Tos(version=2, text="Test 2", current=True, role=role)
        new_TOS.save()

        self.browser.get(self.live_server_url + "/login")
        assert "Terms of Service" in self.browser.page_source

        button = self.browser.find_element_by_id("tos-accept")
        button.click()

        # Teacher generally redirected to account if logged in
        self.browser.get(self.live_server_url + "/login")

        assert "My Account" in self.browser.page_source

        # Teacher can create a question
        self.browser.find_element_by_id("question-section").click()
        self.browser.find_element_by_link_text("Create new").click()

        time.sleep(1)

        assert "Step 1" in self.browser.find_element_by_tag_name("h2").text

        inputbox = self.browser.find_element_by_id("id_title")
        inputbox.send_keys("Test title")

        tinymce_embed = self.browser.find_element_by_tag_name("iframe")
        self.browser.switch_to_frame(tinymce_embed)
        ifrinputbox = self.browser.find_element_by_id("tinymce")
        ifrinputbox.send_keys("Test text")
        self.browser.switch_to_default_content()

        inputbox.submit()

        assert "Step 2" in self.browser.find_element_by_tag_name("h2").text

        tinymce_embed = self.browser.find_element_by_id(
            "id_answerchoice_set-0-text_ifr"
        )
        self.browser.switch_to_frame(tinymce_embed)
        ifrinputbox = self.browser.find_element_by_id("tinymce")
        ifrinputbox.send_keys("Answer 1")
        self.browser.switch_to_default_content()

        tinymce_embed = self.browser.find_element_by_id(
            "id_answerchoice_set-1-text_ifr"
        )
        self.browser.switch_to_frame(tinymce_embed)
        ifrinputbox = self.browser.find_element_by_id("tinymce")
        ifrinputbox.send_keys("Answer 2")
        self.browser.switch_to_default_content()

        self.browser.find_element_by_id(
            "id_answerchoice_set-0-correct"
        ).click()

        inputbox = self.browser.find_element_by_id("answer-choice-form")

        inputbox.submit()

        print(Question.objects.get(title="Test title").created_on)

        assert "Step 3" in self.browser.find_element_by_tag_name("h2").text

        self.browser.find_element_by_id("add_question_to_assignment").submit()

        time.sleep(1)

        assert "My Account" in self.browser.find_element_by_tag_name("h1").text
        assert "Test title" in self.browser.page_source

        # Teacher can edit their questions
        self.browser.find_element_by_id("question-section").click()
        time.sleep(1)
        question = Question.objects.get(title="Test title")
        self.browser.find_element_by_id(
            "edit-question-" + str(question.id)
        ).click()

        assert "Step 1" in self.browser.find_element_by_tag_name("h2").text

        tinymce_embed = self.browser.find_element_by_tag_name("iframe")
        self.browser.switch_to_frame(tinymce_embed)
        ifrinputbox = self.browser.find_element_by_id("tinymce")
        ifrinputbox.send_keys("Edited: ")
        self.browser.switch_to_default_content()

        inputbox = self.browser.find_element_by_id("id_title")
        inputbox.submit()

        question.refresh_from_db()

        assert "Step 2" in self.browser.find_element_by_tag_name("h2").text
        assert "Edited: Test text" in question.text

        # Teacher cannot edit another teacher's questions
        self.browser.get(
            self.live_server_url
            + reverse("question-update", kwargs={"pk": 43})
        )
        assert "Forbidden" in self.browser.page_source

        # Teacher can create an assignment
        self.browser.get(
            self.live_server_url + reverse("teacher", kwargs={"pk": 1})
        )
        self.browser.find_element_by_id("assignment-section").click()
        self.browser.find_element_by_link_text("Manage assignments").click()
        assert "Create a new assignment" in self.browser.page_source

        inputbox = self.browser.find_element_by_id("id_identifier")
        inputbox.send_keys("New unique assignment identifier")

        inputbox = self.browser.find_element_by_id("id_title")
        inputbox.send_keys("New assignment title")

        inputbox.submit()

        assert "New unique assignment identifier" in self.browser.page_source
        assert (
            Assignment.objects.filter(
                identifier="New unique assignment identifier"
            ).count()
            == 1
        )

        # Teacher can edit an assignment

        # Teacher can create a blink assignment

        # Teacher can delete a blink assignment

        # Teacher can edit a blink assignment

        # Access account from link in top right corner

        # Teacher cannot access other teacher accounts
        self.browser.get(
            self.live_server_url + reverse("teacher", kwargs={"pk": 2})
        )
        assert "Forbidden" in self.browser.page_source

        # Teacher declines TOS

        # Checkout what answer choice form looks like if student answers

        # Teacher cannot delete any questions

        # Need a test to assert reset question never appears in LTI

        # Teacher clones: check new and old question states including answer_choices
