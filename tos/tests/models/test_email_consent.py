from datetime import datetime

import pytz

from tos.models import EmailConsent

from ..fixtures import *  # noqa
from ..generators import new_email_consents


def test_new_email_consent(email_types, users):
    data = new_email_consents(
        4, users, email_types, all_combinations_present=True
    )

    for d in data:
        time = datetime.now(pytz.utc)
        consent = EmailConsent.objects.create(**d)
        assert isinstance(consent, EmailConsent)
        assert consent.user.username == d["user"].username
        assert consent.email_type.role == d["email_type"].role
        assert consent.email_type.type == d["email_type"].type
        assert consent.accepted == d["accepted"]
        assert consent.datetime > time
        assert consent.datetime < datetime.now(pytz.utc)


def test_get_email_consent(email_consents, users, email_types):

    tests = [
        {
            "username": user.username,
            "email_type": email_type.type,
            "role": email_type.role.role,
        }
        for user in users
        for email_type in email_types
    ]

    for test in tests:
        consent = EmailConsent.get(**test)
        assert isinstance(consent, bool)
        corrects = [
            c
            for c in EmailConsent.objects.filter(
                user__username=test["username"],
                email_type__type=test["email_type"],
                email_type__role=test["role"],
            ).order_by("-datetime")
        ]
        for correct in corrects[1:]:
            assert corrects[0].datetime > correct.datetime
        assert consent == corrects[0].accepted


def test_get_email_consent_doesnt_exist(email_consents, users, email_types):
    EmailConsent.objects.filter(user=users[1]).delete()
    EmailConsent.objects.filter(email_type=email_types[1]).delete()

    tests = [
        {
            "username": users[-1].username,
            "email_type": email_type.type,
            "role": email_type.role.role,
        }
        for email_type in email_types
    ]

    for test in tests:
        consent = EmailConsent.get(**test)
        assert consent is None
