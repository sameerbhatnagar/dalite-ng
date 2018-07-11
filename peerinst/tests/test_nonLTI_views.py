
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase

import peerinst.views

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
