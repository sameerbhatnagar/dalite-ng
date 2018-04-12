from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_custom_settings_static_files(self):
        self.browser.get(self.live_server_url)
        self.assertIn('myDALITE',self.browser.title)
        self.fail('finish the test')