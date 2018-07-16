from django.contrib.auth.hashers import make_password
from django.test import LiveServerTestCase
from selenium import webdriver

from django_lti_tool_provider.models import LtiUserData
from django_lti_tool_provider.views import LTIView
from peerinst.models import User, Teacher

from django.test.utils import override_settings

from peerinst.tests.test_views import QuestionViewTestCase

class NewStudentConsentTest(QuestionViewTestCase):
    fixtures = ['test_users.yaml']


    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)


    def tearDown(self):
        self.browser.quit()

    def test_login_through_lti(self):
        """Log a user in with fake LTI data."""
        response = self.question_get()
        self.assertTemplateUsed(response, 'peerinst/question_start.html')       


