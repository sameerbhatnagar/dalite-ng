from django.core.urlresolvers import reverse
from .test_views import QuestionViewTestCase
from peerinst.models import Student

class NewStudentConsentTest(QuestionViewTestCase):

    def test_consent_unseen_student(self):
        """test Consent form shown to new students in LTI"""
        new_student = Student(
            student=self.user
        )
        new_student.save()
        self.assertTrue(new_student.student.is_authenticated())
        response = self.question_get()
        # This will raise error in tos models.py as no TOS exists
        self.assertEqual(response.status_code, 500)

        # Add TOS
        from tos.models import Tos
        new_TOS = Tos(
            version = 1,
            hash = 'asdfasfas',
            text = 'Test',
            current = True,
            role = 'st',
        )
        new_TOS.save()
        response = self.question_get()
        self.assertRedirects(response, reverse("tos:consent", kwargs={ 'role' : 'student'}) + "?next=" + self.question_url, status_code=302, target_status_code=200)
