from django.core.urlresolvers import reverse
from .test_views import QuestionViewTestCase

class NewStudentConsentTest(QuestionViewTestCase):
    fixtures = ['test_users.yaml']

    def test_consent_unseen_student(self):
        """test Consent form shown to new students in LTI"""
        response = self.question_get()
        self.assertRedirects(response, reverse('tos:modify', args=("student",)),status_code=302, target_status_code=200)       


