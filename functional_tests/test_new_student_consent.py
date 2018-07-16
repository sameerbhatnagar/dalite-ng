from selenium import webdriver

from peerinst.tests.test_views import QuestionViewTestCase

class NewStudentConsentTest(QuestionViewTestCase):
    fixtures = ['test_users.yaml']


    def setUp(self):
        super(NewStudentConsentTest,self).setUp()        
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)


    def tearDown(self):
        self.browser.quit()

    def test_login_through_lti(self):
        """Log a user in with fake LTI data."""
        response = self.question_get()
        self.assertTemplateUsed(response, 'peerinst/question_start.html')       


