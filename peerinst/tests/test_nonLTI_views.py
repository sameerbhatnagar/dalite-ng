from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase, TransactionTestCase

from ..models import Discipline, Question, User, Teacher

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

    def setUp(self):
        self.user = 'validated_teacher'
        self.password = 'ssdfl_adfga89'
        user = User.objects.create(username=self.user, password=make_password(self.password), is_active=True)
        teacher = Teacher.objects.create(user=user)

        self.other = 'other_teacher'
        self.other_password = 'sssdfDSASDdfga89'
        user = User.objects.create(username=self.other, password=make_password(self.other_password), is_active=True)
        teacher = Teacher.objects.create(user=user)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Teacher.objects.count(), 2)

    def test_login_and_access_to_accounts(self):
        # Login
        response = self.client.post(reverse('login'), {'username' : self.user, 'password' : self.password}, follow=True)
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
