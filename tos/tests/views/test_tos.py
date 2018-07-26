from __future__ import unicode_literals
import json
import random

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from tos.models import Tos
from ..test_models import (
    _add_consents,
    _add_tos,
    _add_users,
    _new_consent,
    _new_tos,
    _new_user,
)
from .utils import login_user


class TestTosConsentView(TestCase):
    def setUp(self):
        self.client = Client()
        n_users = 1
        n_tos = 1
        n_consent = 1
        self.users = _add_users(_new_user(n_users))
        self.tos = _add_tos(_new_tos(n_tos))
        self.consents = _new_consent(n_consent, self.users, self.tos)
        for user in self.users:
            login_user(self.client, user)

    def test_consent_exists_and_is_true(self):
        self.consents[0]["accepted"] = True
        _add_consents(self.consents)

        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0]
            },
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_consent", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            body = json.loads(resp.content)
            self.assertEqual(body["consent"], True)

    def test_consent_exists_and_is_false(self):
        self.consents[0]["accepted"] = False
        _add_consents(self.consents)

        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0]
            },
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_consent", kwargs=test))
            body = json.loads(resp.content)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(body["consent"], False)

    def test_consent_doesnt_exist_yet(self):
        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0]
            },
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_consent", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/tos_modify.html")

    def test_consent_version_doesnt_exist(self):
        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version) + 1,
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_consent", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test["version"], test["role"]),
                resp.content,
            )

    def test_consent_wrong_method(self):
        tests = [{"role": Tos.ROLES[0]}]
        for test in tests:
            resp = self.client.post(reverse("tos:tos_consent", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_invalid_role(self):
        tests = [{"role": Tos.ROLES[0] + "fdsa"}]
        for test in tests:
            resp = self.client.get(reverse("tos:tos_consent", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                '"{}" isn\'t a valid role.'.format(test["role"]), resp.content
            )


class TestTosConsentModifyView(TestCase):
    def setUp(self):
        self.client = Client()
        n_users = 1
        n_tos = 1
        n_consent = 1
        self.users = _add_users(_new_user(n_users))
        self.tos = _add_tos(_new_tos(n_tos))
        self.consents = _new_consent(n_consent, self.users, self.tos)
        for user in self.users:
            login_user(self.client, user)

    def test_consent_modify(self):
        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version),
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_modify", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/tos_modify.html")

    def test_consent_modify_already_exists(self):
        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version),
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_modify", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/tos_modify.html")

    def test_consent_modify_version_doesnt_exist(self):
        tests = [
            {
                "role": [
                    r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                ][0],
                "version": int(self.tos[0].version) + 1,
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:tos_modify", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test["version"], test["role"]),
                resp.content,
            )

    def test_consent_modify_wrong_method(self):
        tests = [{"role": Tos.ROLES[0], "version": 0}]
        for test in tests:
            resp = self.client.post(reverse("tos:tos_modify", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_modify_invalid_role(self):
        tests = [{"role": Tos.ROLES[0] + "fdsa", "version": 0}]
        for test in tests:
            resp = self.client.get(reverse("tos:tos_modify", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                '"{}" isn\'t a valid role.'.format(test["role"]), resp.content
            )


class TestTosConsentUpdateView(TestCase):
    def setUp(self):
        self.client = Client()
        n_users = 1
        n_tos = 1
        n_consent = 1
        self.users = _add_users(_new_user(n_users))
        self.tos = _add_tos(_new_tos(n_tos, role="student")) + _add_tos(
            _new_tos(n_tos, role="teacher")
        )
        self.consents = _new_consent(n_consent, self.users, self.tos)
        for user in self.users:
            login_user(self.client, user)

    def test_consent_update_accepted(self):
        tests = [
            (
                {
                    "role": [
                        r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                    ][0],
                    "version": int(self.tos[0].version),
                },
                {"accepted": True},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:tos_update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, "/welcome/", target_status_code=302)

    def test_consent_update_refused(self):
        tests = [
            (
                {
                    "role": [
                        r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                    ][0],
                    "version": int(self.tos[0].version),
                },
                {"accepted": False},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:tos_update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, "/welcome/", target_status_code=302)

    def test_consent_update_redirect(self):
        tests = [
            (
                {
                    "role": next(
                        r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                    ),
                    "version": int(self.tos[0].version),
                },
                {"accepted": True, "redirect_to": "/tos/tos/student/"},
            )
        ]
        print(self.tos)
        print(self.consents)

        print(Tos.objects.all())
        for test in tests:
            resp = self.client.post(
                reverse("tos:tos_update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(
                resp, "/tos/tos/student/", target_status_code=200
            )

    def test_consent_update_version_doesnt_exist(self):
        tests = [
            (
                {
                    "role": [
                        r for r in Tos.ROLES if r.startswith(self.tos[0].role)
                    ][0],
                    "version": int(self.tos[0].version) + 1,
                },
                {"accepted": random.random() > 0.5},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:tos_update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test[0]["version"], test[0]["role"]),
                resp.content,
            )

    def test_consent_update_wrong_method(self):
        tests = [{"role": Tos.ROLES[0], "version": 0}]
        for test in tests:
            resp = self.client.get(reverse("tos:tos_update", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_update_invalid_role(self):
        tests = [
            (
                {"role": Tos.ROLES[0] + "fdsa", "version": 0},
                {"accepted": random.random() > 0.5},
            )
        ]
        for test in tests:
            resp = self.client.post(
                reverse("tos:tos_update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                '"{}" isn\'t a valid role.'.format(test[0]["role"]),
                resp.content,
            )
