import json
import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Tos
from .test_models import (
    _add_consents,
    _add_tos,
    _add_users,
    _new_consent,
    _new_tos,
    _new_user,
)


class TestConsentView(TestCase):
    def test_consent_exists_and_is_true(self):
        n_users = 1
        n_tos = 1
        n_consent = 1
        users = _add_users(_new_user(n_users))
        tos = _add_tos(_new_tos(n_tos))
        consents = _new_consent(n_consent, users, tos)
        consents[0]["accepted"] = True
        _add_consents(consents)

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
            },
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            body = json.loads(resp.content)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(body["consent"], True)

    def test_consent_exists_and_is_false(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))
        n_consent = 1
        consents = _new_consent(n_consent, users, tos)
        consents[0]["accepted"] = False
        _add_consents(consents)

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
            },
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            body = json.loads(resp.content)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(body["consent"], False)

    def test_consent_doesnt_exist_yet(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
            },
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/consent.html")

    def test_consent_user_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username + "fdajnfdajfna",
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
            },
            {
                "username": users[0].username + "fdajnfdajfna",
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn("User doesn't exist", resp.content)

    def test_consent_version_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version) + 1,
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test["version"], test["role"]),
                resp.content,
            )

    def test_consent_wrong_method(self):
        tests = [{"username": "fsajgsjlg", "role": Tos.ROLES[0]}]
        for test in tests:
            resp = self.client.post(reverse("tos:consent", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_invalid_role(self):
        tests = [{"username": "fsajgsjlg", "role": Tos.ROLES[0] + "fdsa"}]
        for test in tests:
            resp = self.client.get(reverse("tos:consent", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn("Not a valid role", resp.content)


class TestConsentModifyView(TestCase):
    def test_consent_modify(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/consent.html")

    def test_consent_modify_already_exists(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            },
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, "tos/consent.html")

    def test_consent_modify_user_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username + "fdajnfdajfna",
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version),
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn("User doesn't exist", resp.content)

    def test_consent_modify_version_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            {
                "username": users[0].username,
                "role": [r for r in Tos.ROLES if r.startswith(tos[0].role)][0],
                "version": int(tos[0].version) + 1,
            }
        ]

        for test in tests:
            resp = self.client.get(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test["version"], test["role"]),
                resp.content,
            )

    def test_consent_modify_wrong_method(self):
        tests = [{"username": "fsajgsjlg", "role": Tos.ROLES[0], "version": 0}]
        for test in tests:
            resp = self.client.post(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_modify_invalid_role(self):
        tests = [
            {
                "username": "fsajgsjlg",
                "role": Tos.ROLES[0] + "fdsa",
                "version": 0,
            }
        ]
        for test in tests:
            resp = self.client.get(reverse("tos:modify", kwargs=test))
            self.assertEqual(resp.status_code, 400)
            self.assertIn("Not a valid role", resp.content)


class TestConsentUpdateView(TestCase):
    def test_consent_update_accepted(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            (
                {
                    "username": users[0].username,
                    "role": [
                        r for r in Tos.ROLES if r.startswith(tos[0].role)
                    ][0],
                    "version": int(tos[0].version),
                },
                {"accepted": True},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You've accepted!", resp.content)

    def test_consent_update_refused(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            (
                {
                    "username": users[0].username,
                    "role": [
                        r for r in Tos.ROLES if r.startswith(tos[0].role)
                    ][0],
                    "version": int(tos[0].version),
                },
                {"accepted": False},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You've refused...", resp.content)

    def test_consent_update_user_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            (
                {
                    "username": users[0].username + "fdajnfdajfna",
                    "role": [
                        r for r in Tos.ROLES if r.startswith(tos[0].role)
                    ][0],
                    "version": int(tos[0].version),
                },
                {"accepted": random.random() > 0.5},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 400)
            self.assertIn("User doesn't exist", resp.content)

    def test_consent_update_version_doesnt_exist(self):
        n_users = 1
        users = _add_users(_new_user(n_users))
        n_tos = 1
        tos = _add_tos(_new_tos(n_tos))

        tests = [
            (
                {
                    "username": users[0].username,
                    "role": [
                        r for r in Tos.ROLES if r.startswith(tos[0].role)
                    ][0],
                    "version": int(tos[0].version) + 1,
                },
                {"accepted": random.random() > 0.5},
            )
        ]

        for test in tests:
            resp = self.client.post(
                reverse("tos:update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 400)
            self.assertIn(
                "There is no terms of service with version "
                '{} for role "{}"'.format(test[0]["version"], test[0]["role"]),
                resp.content,
            )

    def test_consent_update_wrong_method(self):
        tests = [{"username": "fsajgsjlg", "role": Tos.ROLES[0], "version": 0}]
        for test in tests:
            resp = self.client.get(reverse("tos:update", kwargs=test))
            self.assertEqual(resp.status_code, 405)

    def test_consent_update_invalid_role(self):
        tests = [
            (
                {
                    "username": "fsajgsjlg",
                    "role": Tos.ROLES[0] + "fdsa",
                    "version": 0,
                },
                {"accepted": random.random() > 0.5},
            )
        ]
        for test in tests:
            resp = self.client.post(
                reverse("tos:update", kwargs=test[0]), test[1]
            )
            self.assertEqual(resp.status_code, 400)
            self.assertIn("Not a valid role", resp.content)
