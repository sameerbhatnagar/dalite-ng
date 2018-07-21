from django.core.urlresolvers import reverse
from .test_views import QuestionViewTestCase
from django.test import TestCase
from peerinst.models import Student
from tos.models import Consent, Tos

class TOSError(QuestionViewTestCase):

    def test_no_tos_exists(self):
        # Delete TOS
        tos = Tos.objects.all().first()
        tos.delete()
        response = self.question_get()
        # This will raise error in tos models.py as no TOS exists and we want custom error page to be rendered with message from app
        self.assertTemplateUsed(response, '500.html')
        self.assertContains(response, 'There is no terms of service yet.', status_code=500)

        # Add TOS
        new_TOS = Tos(
            version = 1,
            text = 'Test',
            current = True,
            role = 'st',
        )
        new_TOS.save()
        response = self.question_get()
        self.assertRedirects(response, reverse("tos:consent", kwargs={ 'role' : 'student'}) + "?next=" + self.question_url, status_code=302, target_status_code=200)


class GetStudentConsent(QuestionViewTestCase):

    def test_student_can_change_consent(self):
        """Test consent form accessible through template"""
        response = self.question_get()
        self.assertContains(response, '/tos/student/modify/')
