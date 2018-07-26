from __future__ import unicode_literals
import json
import random

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from tos.models import Role, EmailType, EmailConsent
from ..generators import (
    add_users,
    add_roles,
    add_email_types,
    add_email_consents,
    new_users,
    new_roles,
    new_email_types,
    new_email_consents,
)
from .utils import login_user


class TestEmailConsentModifyView(TestCase):
    def setUp(self):
        self.client = Client()
        n_users = 1
        n_roles = 1
        n_email_types = 1
        n_consents = 1
        self.users = add_users(new_users(n_users))
        self.roles = add_roles(new_roles(n_roles))
        self.email_types = add_email_types(
            new_email_types(n_email_types, self.roles)
        )
        self.consents = new_email_consents(
            n_consents, self.users, self.email_types
        )
        for user in self.users:
            login_user(self.client, user)

    def test_consent_modify(self):
        tests = [{"role": role.role} for role in self.roles]

        for test in tests:
            print(reverse("tos:email_modify", kwargs=test))
            resp = self.client.get(reverse("tos:email_modify", kwargs=test))
            print(resp)
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/email_modify.html")
