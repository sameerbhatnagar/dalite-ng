from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase, TransactionTestCase

from ..models import Discipline, Question, Assignment, User, Teacher, Student

class LandingPageTest(TransactionTestCase):

    def setUp(self):
        physics = Discipline.objects.create(title='Physics')
        math = Discipline.objects.create(title='Math')
        chemistry = Discipline.objects.create(title='Chemistry')

        Question.objects.create(title='A', text='text', discipline=physics)
        Question.objects.create(title='B', text='text', discipline=physics)
        Question.objects.create(title='C', text='text', discipline=physics)

        Question.objects.create(title='D', text='text', discipline=math)
        Question.objects.create(title='E', text='text', discipline=math)

        Question.objects.create(title='F', text='text', discipline=chemistry)

    def test_discipline_stats(self):
        self.assertEqual(Question.objects.count(), 6)
        self.assertEqual(Discipline.objects.count(), 3)

        response = self.client.get(reverse('landing_page'))

        self.assertEqual(response.context['disciplines'][0]['name'], 'All')
        self.assertEqual(response.context['disciplines'][1]['name'], 'Physics')
        self.assertEqual(response.context['disciplines'][2]['name'], 'Math')
        self.assertEqual(response.context['disciplines'][3]['name'], 'Chemistry')


class SignUpTest(TestCase):

    def test_which_template(self):
        response = self.client.get(reverse('sign_up'))
        self.assertTemplateUsed(response, 'registration/sign_up.html')

    def test_invalid_form_post(self):
        response = self.client.post(reverse('sign_up'), data={})
        self.assertIn('This field is required', response.content.decode())

    def test_valid_form_post(self):
        response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath4', 'email':'abc@def.com', 'url':'http://abc.com'})
        self.assertTemplateUsed(response, 'registration/sign_up_done.html')
        self.assertTemplateUsed(response, 'registration/sign_up_admin_email_html.html')

    def test_password_mismatch(self):
        response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath', 'email':'abc@def.com', 'url':'http://abc.com'})
        self.assertIn('The two password fields didn\'t match', response.content.decode())

    def test_email_error(self):

        with self.settings(EMAIL_BACKEND=''):
            response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath4', 'email':'abc@def.com', 'url':'http://abc.com'}, follow=True)
            self.assertEqual(response.status_code, 500)
            self.assertTemplateUsed(response, '500.html')


class TeacherTest(TestCase):
    fixtures = ['test_users.yaml', 'peerinst_test_data.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.user.text_pwd = self.user.password
        self.user.password = make_password(self.user.text_pwd)
        self.user.save()

    def test_login_and_access_to_accounts(self):
        # Login
        response = self.client.post(reverse('login'), {'username' : self.user.username, 'password' : self.user.text_pwd}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk, 1)
        self.assertTemplateUsed(response, 'peerinst/teacher_detail.html')

        # Test access to other
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 2 }))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

        # Test access to non-existent
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 3 }))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        # Logout
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/landing_page.html')

        # Attempt access after logout
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 1 }), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_question_list_view(self):
        logged_in = self.client.login(username=self.user.username, password=self.user.text_pwd)
        self.assertTrue(logged_in)

        # List matches assignment object
        response = self.client.get(reverse('question-list', kwargs={ 'assignment_id' : 'Assignment1' }))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.context['object_list'], Assignment.objects.get(pk='Assignment1').questions.all())

        # Assignment pk invalid -> 404
        response = self.client.get(reverse('question-list', kwargs={ 'assignment_id' : 'unknown_id' }))
        self.assertEqual(response.status_code, 404)

    def test_assignment_update(self):
        logged_in = self.client.login(username=self.user.username, password=self.user.text_pwd)
        self.assertTrue(logged_in)

        self.fail()


class StudentTest(TestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=10)
        self.user.text_pwd = self.user.password
        self.user.password = make_password(self.user.text_pwd)
        self.user.save()

    def test_login_to_web_app(self):
        # Login -> 403 & forced logout
        response = self.client.post(reverse('login'), {'username' : self.user.username, 'password' : self.user.text_pwd}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        response = self.client.post(reverse('assignment-list'))
        self.assertRedirects(response, reverse('login')+'?next=/assignment-list/')

    def test_login_and_answer_question(self):
        pass
