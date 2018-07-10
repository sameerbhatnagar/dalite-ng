from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        print('Open browser')
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_new_user(self):
        print('Navigate to '+self.live_server_url+'/signup')
        self.browser.get(self.live_server_url+'/signup')

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

        time.sleep(10)

        # New user redirected post sign up
        self.assertIn('Processing request', self.browser.find_element_by_tag_name('h1').text)

        # New user cannot sign in
        self.browser.get(self.live_server_url+'/login')
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys('test')

        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys('jka+sldfa+soih')

        inputbox.send_keys(Keys.ENTER)

        time.sleep(1)

        assert "your account has not yet been activated" in self.browser.page_source

    def __test_validated_user(self):
        self.browser.get(self.live_server_url)

        # Validated user can login

        # Validated user can browse certain pages

        # Validated user cannot access account

        # Validated user can logout

    def __test_teacher(self):
        self.browser.get(self.live_server_url)

        # Teacher can login

        # Teacher can access account

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
