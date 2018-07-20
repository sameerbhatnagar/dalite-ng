from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

from django.contrib.auth.models import Permission, Group
from peerinst.models import User, Teacher, Question, Assignment
from tos.models import Tos

def ready_user(pk):
    user = User.objects.get(pk=pk)
    user.text_pwd = user.password
    user.password = make_password(user.text_pwd)
    user.save()
    return user

class NewUserTests(StaticLiveServerTestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

        self.validated_teacher = ready_user(1)
        self.inactive_user = ready_user(3)

        self.group = Group.objects.get(name="Teacher")
        self.assertFalse(self.group.permissions.all())

        permission = Permission.objects.get(codename='add_question')
        self.group.permissions.add(permission)
        permission = Permission.objects.get(codename='change_question')
        self.group.permissions.add(permission)
        self.assertEqual(self.group.permissions.count(), 2)

        self.assertFalse(self.validated_teacher.get_all_permissions())

        # Add TOS for teachers
        new_TOS = Tos(
            version = 1,
            text = 'Test',
            current = True,
            role = 'te',
        )
        new_TOS.save()


    def tearDown(self):
        self.browser.quit()


    def test_new_user(self):
        # Hit landing page
        self.browser.get(self.live_server_url+'/#Features')
        self.assertIn('Features', self.browser.find_element_by_tag_name('h1').text)
        self.assertIn('Login', self.browser.find_element_by_id('link-to-login-or-welcome').text)
        self.browser.find_element_by_link_text('Signup').click()

        # Sign up page rendered
        self.assertIn('Sign Up', self.browser.find_element_by_tag_name('h1').text)

        # New user can sign up
        form = self.browser.find_element_by_tag_name('form')
        self.assertEqual(form.get_attribute("method"), "post")

        inputbox = self.browser.find_element_by_id('id_email')
        inputbox.send_keys('test@test.com')

        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys('test')

        inputbox = self.browser.find_element_by_id('id_password1')
        inputbox.send_keys('jka+sldfa+soih')

        inputbox = self.browser.find_element_by_id('id_password2')
        inputbox.send_keys('jka+sldfa+soih')

        inputbox = self.browser.find_element_by_id('id_url')
        inputbox.clear()
        inputbox.send_keys('http://www.mydalite.org')

        inputbox.submit()

        # New user redirected post sign up
        self.assertIn('Processing Request', self.browser.find_element_by_tag_name('h1').text)

        # New user cannot sign in
        self.browser.get(self.live_server_url+'/login')
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys('test')

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys('jka+sldfa+soih')

        inputbox.submit()

        # Small pause to see last page
        time.sleep(1)

        assert "your account has not yet been activated" in self.browser.page_source


    def test_new_user_with_email_server_error(self):

        with self.settings(EMAIL_BACKEND=''):
            self.browser.get(self.live_server_url+'/signup')

            form = self.browser.find_element_by_tag_name('form')
            self.assertEqual(form.get_attribute("method"), "post")

            inputbox = self.browser.find_element_by_id('id_email')
            inputbox.send_keys('test@test.com')

            inputbox = self.browser.find_element_by_id('id_username')
            inputbox.send_keys('test')

            inputbox = self.browser.find_element_by_id('id_password1')
            inputbox.send_keys('jka+sldfa+soih')

            inputbox = self.browser.find_element_by_id('id_password2')
            inputbox.send_keys('jka+sldfa+soih')

            inputbox = self.browser.find_element_by_id('id_url')
            inputbox.clear()
            inputbox.send_keys('http://www.mydalite.org')

            inputbox.submit()

            time.sleep(1)

            assert "500" in self.browser.page_source


    def test_inactive_user_login(self):
        self.browser.get(self.live_server_url+'/login')

        # Inactive user cannot login
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys(self.inactive_user.username)

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys(self.inactive_user.text_pwd)

        inputbox.submit()

        time.sleep(1)

        assert "your account has not yet been activated" in self.browser.page_source


    def __test_validated_user(self):
        # Validated user can login
        self.browser.get(self.live_server_url+'/login')

        # Validated user can browse certain pages

        # Validated user cannot access account

        # Validated user can logout


    def test_teacher(self):
        # Teacher can login and access account
        self.browser.get(self.live_server_url+'/login')
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys(self.validated_teacher.username)

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys(self.validated_teacher.text_pwd)

        inputbox.submit()

        time.sleep(1)

        assert "Terms of Service" in self.browser.page_source

        button = self.browser.find_element_by_id('tos-accept')
        button.click()

        assert "My Account" in self.browser.page_source
        assert "Terms of service: Sharing" in self.browser.page_source

        # Logout and log back in -> skip tos
        self.browser.get(self.live_server_url+'/logout')
        self.browser.get(self.live_server_url+'/login')
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys(self.validated_teacher.username)

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys(self.validated_teacher.text_pwd)

        inputbox.submit()

        time.sleep(1)
        assert "My Account" in self.browser.page_source

        # Add a new current TOS for teachers and refresh account -> tos
        new_TOS = Tos(
            version = 2,
            text = 'Test 2',
            current = True,
            role = 'te',
        )
        new_TOS.save()

        self.browser.get(self.live_server_url+'/login')
        assert "Terms of Service" in self.browser.page_source

        button = self.browser.find_element_by_id('tos-accept')
        button.click()

        # Teacher generally redirected to account if logged in
        self.browser.get(self.live_server_url+'/login')

        assert "My Account" in self.browser.page_source

        # Teacher can create a question
        self.browser.find_element_by_link_text('Create new').click()

        time.sleep(1)

        assert "Step 1" in self.browser.find_element_by_tag_name('h2').text

        inputbox = self.browser.find_element_by_id('id_title')
        inputbox.send_keys('Test title')

        inputbox = self.browser.find_element_by_id('id_text')
        inputbox.send_keys('Test text')

        inputbox.submit()

        assert "Step 2" in self.browser.find_element_by_tag_name('h2').text

        inputbox = self.browser.find_element_by_id('id_answerchoice_set-0-text')
        inputbox.send_keys('Answer 1')

        inputbox = self.browser.find_element_by_id('id_answerchoice_set-1-text')
        inputbox.send_keys('Answer 2')

        self.browser.find_element_by_id('id_answerchoice_set-0-correct').click()

        inputbox.submit()

        assert "Step 3" in self.browser.find_element_by_tag_name('h2').text

        form = self.browser.find_element_by_id('add_question_to_assignment').submit()

        assert "My Account" in self.browser.find_element_by_tag_name('h1').text
        assert "Test title" in self.browser.page_source

        # Teacher can edit their questions
        question = Question.objects.get(title='Test title')
        edit_button = self.browser.find_element_by_id('edit-question-'+str(question.id)).click()

        assert "Step 1" in self.browser.find_element_by_tag_name('h2').text

        inputbox = self.browser.find_element_by_id('id_text')
        inputbox.send_keys(' edited')

        inputbox.submit()

        question.refresh_from_db()

        assert "Step 2" in self.browser.find_element_by_tag_name('h2').text
        assert "Test text edited" in question.text

        # Teacher cannot edit another teacher's questions
        self.browser.get(self.live_server_url + reverse('question-update', kwargs={ 'pk' : 43 }))
        assert "Forbidden" in self.browser.page_source

        # Teacher can create an assignment
        self.browser.get(self.live_server_url + reverse('teacher', kwargs={ 'pk' : 1 } ))
        manage_assignments_button = self.browser.find_element_by_link_text('Manage assignments').click()
        assert "Create a new assignment" in self.browser.page_source

        inputbox = self.browser.find_element_by_id('id_identifier')
        inputbox.send_keys('New unique assignment identifier')

        inputbox = self.browser.find_element_by_id('id_title')
        inputbox.send_keys('New assignment title')

        inputbox.submit()

        assert "New unique assignment identifier" in self.browser.page_source
        assert Assignment.objects.filter(identifier="New unique assignment identifier").count() == 1

        # Teacher can edit an assignment

        # Teacher can create a blink assignment

        # Teacher can delete a blink assignment

        # Teacher can edit a blink assignment

        # Access account from link in top right corner

        # Welcome authenticated user on landing pages
        self.browser.get(self.live_server_url)
        welcome = self.browser.find_element_by_id('link-to-login-or-welcome')
        assert "Welcome back "+self.validated_teacher.username in welcome.text

        # Teacher cannot access other teacher accounts
        self.browser.get(self.live_server_url + reverse('teacher', kwargs={ 'pk' : 2 } ))
        assert "Forbidden" in self.browser.page_source



        # Checkout what answer choice form looks like if student answers

        # Teacher cannot delete any questions

        # Need a test to assert reset question never appears in LTI

        # Teacher clones: check new and old question states including answer_choices
