from __future__ import unicode_literals

import random
import string
from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from tos.models import Consent as TosConsent
from tos.models import EmailConsent, EmailType, Tos, _compute_hash

from .generators import (
    add_email_consents,
    add_email_types,
    add_roles,
    add_tos,
    add_tos_consents,
    add_users,
    new_email_consents,
    new_email_types,
    new_roles,
    new_tos,
    new_tos_consents,
    new_users,
)


class TestTosModel(TestCase):
    def test_new_tos(self):
        n = 5
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        data = new_tos(n, roles, all_roles_present=True, random_current=True)
        first_for_role = {role: True for role in roles}

        for d in data:
            time = datetime.now(pytz.utc)
            tos = Tos.objects.create(**d)
            self.assertIsInstance(tos, Tos)
            self.assertEqual(tos.role, d["role"])
            self.assertEqual(tos.version, d["version"])
            self.assertEqual(tos.text, d["text"])
            if first_for_role[d["role"]]:
                self.assertEqual(tos.current, True)
                first_for_role[d["role"]] = False
            else:
                self.assertEqual(tos.current, d["current"])
            self.assertEqual(tos.hash, _compute_hash(d["text"]))
            self.assertGreater(tos.created, time)
            self.assertLess(tos.created, datetime.now(pytz.utc))

    def test_new_tos_version_exists(self):
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        data = new_tos(2, roles=roles[0]) + new_tos(1, roles=roles[1])
        data[1]["version"] = data[0]["version"]
        data[2]["version"] = data[0]["version"]

        Tos.objects.create(**data[0])
        Tos.objects.create(**data[2])
        self.assertRaises(IntegrityError, Tos.objects.create, **data[1])

    def test_new_tos_hash_exists(self):
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        data = new_tos(2, roles=roles[0]) + new_tos(1, roles=roles[1])
        data[1]["text"] = data[0]["text"]
        data[2]["text"] = data[0]["text"]

        Tos.objects.create(**data[0])
        Tos.objects.create(**data[2])
        self.assertRaises(IntegrityError, Tos.objects.create, **data[1])

    def test_get_tos(self):
        n_per_role = 5
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        n = n_per_role * len(roles)
        tos_ = add_tos(new_tos(n, roles, all_roles_present=True))
        tests = [
            {"role": role.role, "version": version}
            for role in roles
            for version in [None] + list(range(n_per_role))
        ]

        for test in tests:
            tos, err = Tos.get(**test)
            self.assertIsInstance(tos, Tos)
            self.assertIs(err, None)
            if test["version"] is None:
                correct = [
                    t
                    for t in tos_
                    if t.role.role == test["role"] and t.current
                ][0]
            else:
                correct = [
                    t
                    for t in tos_
                    if t.role.role == test["role"]
                    and t.version == test["version"]
                ][0]
            self.assertEqual(tos.version, correct.version)
            self.assertEqual(tos.role, correct.role)
            self.assertEqual(tos.version, correct.version)
            self.assertEqual(tos.hash, correct.hash)
            self.assertEqual(tos.text, correct.text)
            self.assertEqual(tos.created, correct.created)

    def test_get_tos_no_version(self):
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        tos_ = add_tos(new_tos(1, roles=roles[0]))
        tests = [{"role": roles[1].role, "version": None}]

        for test in tests:
            tos, err = Tos.get(**test)
            self.assertIs(tos, None)
            self.assertEqual(
                err,
                'No terms of service exist yet for role "{}".'.format(
                    test["role"]
                ),
            )

    def test_get_tos_version_doesnt_exist(self):
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        tos_ = add_tos(new_tos(1, roles=roles[0]))
        tests = [{"role": roles[0].role, "version": len(tos_)}]

        for test in tests:
            tos, err = Tos.get(**test)
            self.assertIs(tos, None)
            self.assertEqual(
                err,
                "There is no terms of service with version "
                '{} for role "{}"'.format(test["version"], test["role"]),
            )


class TestTosConsentModel(TestCase):
    def test_new_tos_consent(self):
        n_users = 10
        n_tos = 5
        n = 30
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        users = add_users(new_users(n_users))
        toss = add_tos(new_tos(n_tos, roles))
        data = new_tos_consents(n, users, toss)

        for d in data:
            time = datetime.now(pytz.utc)
            consent = TosConsent.objects.create(**d)
            self.assertIsInstance(consent, TosConsent)
            self.assertEqual(consent.user.username, d["user"].username)
            self.assertEqual(consent.tos.role, d["tos"].role)
            self.assertEqual(consent.tos.version, d["tos"].version)
            self.assertEqual(consent.accepted, d["accepted"])
            self.assertGreater(consent.datetime, time)
            self.assertLess(consent.datetime, datetime.now(pytz.utc))

    def test_get_tos_consent(self):
        n_users = 10
        n_per_role = 2
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        n_tos = n_per_role * len(roles)
        n_per_combination = 2
        n = n_per_combination * n_users * n_tos
        users = add_users(new_users(n_users))
        toss = add_tos(new_tos(n_tos, roles, all_roles_present=True))
        consents = add_tos_consents(
            new_tos_consents(n, users, toss, all_combinations_present=True)
        )

        tests = [
            {"username": user.username, "role": role.role, "version": version}
            for user in users
            for role in roles
            for version in [None] + list(range(n_per_role))
        ]

        for i, test in enumerate(tests):
            print("Failed at test: {}".format(i))
            consent = TosConsent.get(**test)
            self.assertIsInstance(consent, bool)
            if test["version"] is None:
                corrects = [
                    c
                    for c in TosConsent.objects.filter(
                        user__username=test["username"],
                        tos__role=test["role"],
                        tos__current=True,
                    ).order_by("-datetime")
                ]
            else:
                corrects = [
                    c
                    for c in TosConsent.objects.filter(
                        user__username=test["username"],
                        tos__role=test["role"],
                        tos__version=test["version"],
                    ).order_by("-datetime")
                ]
            for correct in corrects[1:]:
                self.assertGreater(corrects[0].datetime, correct.datetime)
            self.assertEqual(consent, corrects[0].accepted)

    def test_get_consent_doesnt_exist(self):
        n_users = 3
        n_per_role = 2
        n_roles = 2
        roles = add_roles(new_roles(n_roles))
        n_tos = n_per_role * len(roles)
        n_per_combination = 2
        n = n_per_combination * n_users * n_tos
        users = add_users(new_users(n_users))
        toss = add_tos(new_tos(n_tos, roles, all_roles_present=True))
        consents = add_tos_consents(
            new_tos_consents(
                n, users[:-1], toss[:-1], all_combinations_present=True
            )
        )
        tests = [
            {
                "username": users[-1].username,
                "role": role.role,
                "version": version,
            }
            for role in roles
            for version in [None] + list(range(n_per_role))
        ] + [
            {
                "username": users[-1].username,
                "role": toss[-1].role.role,
                "version": toss[-1].version,
            }
            for user in users
        ]

        for test in tests:
            consent = TosConsent.get(**test)
            self.assertIs(consent, None)


class TestEmailTypeModel(TestCase):
    def test_new_email_type(self):
        n_roles = 1
        n = 3
        roles = add_roles(new_roles(n_roles))
        data = new_email_types(n, roles)

        for i, d in enumerate(data):
            email_type = EmailType.objects.create(**d)
            self.assertIsInstance(email_type, EmailType)
            self.assertEqual(email_type.role.role, d["role"].role)
            self.assertEqual(email_type.type, d["type"])
            self.assertEqual(email_type.title, d["title"])
            self.assertEqual(email_type.description, d["description"])
            self.assertEqual(email_type.show_order, i + 1)


class TestEmailConsentModel(TestCase):
    def test_new_email_consent(self):
        n_users = 5
        n_roles = 2
        n_per_type = 3
        n_overlapping_types = 1
        n = n_users * n_roles * n_per_type
        users = add_users(new_users(n_users))
        roles = add_roles(new_roles(n_roles))
        email_types = add_email_types(
            new_email_types(
                n_per_type, roles, n_overlapping_types=n_overlapping_types
            )
        )
        data = new_email_consents(
            n, users, email_types, all_combinations_present=True
        )

        for d in data:
            time = datetime.now(pytz.utc)
            consent = EmailConsent.objects.create(**d)
            self.assertIsInstance(consent, EmailConsent)
            self.assertEqual(consent.user.username, d["user"].username)
            self.assertEqual(consent.email_type.role, d["email_type"].role)
            self.assertEqual(consent.email_type.type, d["email_type"].type)
            self.assertEqual(consent.accepted, d["accepted"])
            self.assertGreater(consent.datetime, time)
            self.assertLess(consent.datetime, datetime.now(pytz.utc))

    def test_get_email_consent(self):
        n_users = 5
        n_roles = 2
        n_per_type = 4
        n_overlapping_types = 1
        n = n_per_type * n_roles * n_users
        users = add_users(new_users(n_users))
        roles = add_roles(new_roles(n_roles))
        email_types = add_email_types(
            new_email_types(
                n_per_type, roles, n_overlapping_types=n_overlapping_types
            )
        )
        consents = add_email_consents(
            new_email_consents(
                n, users, email_types, all_combinations_present=True
            )
        )

        tests = [
            {
                "username": user.username,
                "email_type": email_type.type,
                "role": email_type.role.role,
            }
            for user in users
            for email_type in email_types
        ]

        for i, test in enumerate(tests):
            print("Failed at test: {}".format(i))
            consent = EmailConsent.get(**test)
            self.assertIsInstance(consent, bool)
            corrects = [
                c
                for c in EmailConsent.objects.filter(
                    user__username=test["username"],
                    email_type__type=test["email_type"],
                    email_type__role=test["role"],
                ).order_by("-datetime")
            ]
            for correct in corrects[1:]:
                self.assertGreater(corrects[0].datetime, correct.datetime)
            self.assertEqual(consent, corrects[0].accepted)

    def test_get_email_consent_doesnt_exist(self):
        n_users = 5
        n_roles = 2
        n_per_type = 4
        n_overlapping_types = 1
        n = n_per_type * n_roles * n_users
        users = add_users(new_users(n_users))
        roles = add_roles(new_roles(n_roles))
        email_types = add_email_types(
            new_email_types(
                n_per_type, roles, n_overlapping_types=n_overlapping_types
            )
        )
        consents = add_email_consents(
            new_email_consents(
                n, users[:-1], email_types[:-1], all_combinations_present=True
            )
        )

        tests = [
            {
                "username": users[-1].username,
                "email_type": email_type.type,
                "role": email_type.role.role,
            }
            for email_type in email_types
        ]

        for i, test in enumerate(tests):
            print("Failed at test: {}".format(i))
            consent = EmailConsent.get(**test)
            self.assertIs(consent, None)
