from django.contrib.auth.hashers import make_password
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

from peerinst.models import User, Teacher

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

        self.user = 'validated_teacher'
        self.password = 'ssdfl_adfga89'
        user = User.objects.create(username=self.user, password=make_password(self.password), is_active=True)
        teacher = Teacher.objects.create(user=user)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Teacher.objects.count(), 1)

    def tearDown(self):
        self.browser.quit()

    def test_new_user(self):
        # Hit landing page
        self.browser.get(self.live_server_url+'/#Features')
        self.assertIn('Features', self.browser.find_element_by_tag_name('h1').text)
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

        assert "your account has not yet been activated" in self.browser.page_source

        # Small pause to see last page
        time.sleep(1)

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

    def __test_validated_user(self):
        # Validated user can login
        self.browser.get(self.live_server_url+'/login')


        # Validated user can browse certain pages

        # Validated user cannot access account

        # Validated user can logout

    def test_teacher(self):
        self.browser.get(self.live_server_url+'/login')

        # Teacher can login and access account
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys(self.user)

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys(self.password)

        inputbox.submit()

        assert "My Account" in self.browser.page_source

        # Teacher cannot access other teacher accounts


        # Teacher can create a blink assignment

        # Teacher can delete a blink assignment

        # Teacher can edit a blink assignment

        # Teacher can create an assignment

        # Teacher can delete an assignment

        # Teacher can edit an assignment

        # Teacher can create a question

        # Teacher can edit their questions

        # Teacher cannot edit other questions

        # Teacher cannot delete any questions
