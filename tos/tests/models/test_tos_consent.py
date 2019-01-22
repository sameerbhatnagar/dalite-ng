from datetime import datetime

import pytz

from tos.models import Consent as TosConsent

from ..fixtures import *  # noqa
from ..generators import new_tos_consents


def test_new_tos_consent(users, toss_multiple_roles):
    data = new_tos_consents(4, users, toss_multiple_roles)

    for d in data:
        time = datetime.now(pytz.utc)
        consent = TosConsent.objects.create(**d)
        assert isinstance(consent, TosConsent)
        assert consent.user.username == d["user"].username
        assert consent.tos.role == d["tos"].role
        assert consent.tos.version == d["tos"].version
        assert consent.accepted == d["accepted"]
        consent.datetime > time
        consent.datetime < datetime.now(pytz.utc)


def test_get_tos_consent(tos_consents, users, roles, toss_multiple_roles):
    tests = [
        {"username": user.username, "role": role.role, "version": version}
        for user in users
        for role in roles
        for version in [None, 0]
    ]

    for test in tests:
        consent = TosConsent.get(**test)
        assert isinstance(consent, bool)
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
            assert corrects[0].datetime > correct.datetime
        assert consent == corrects[0].accepted


def test_get_tos_consent__doesnt_exist(tos_consents, users, roles):
    TosConsent.objects.filter(user=users[1], tos__role=roles[0]).delete()
    TosConsent.objects.filter(user=users[0], tos__role=roles[1]).delete()
    tests = [
        {
            "username": users[1].username,
            "role": roles[0].role,
            "version": version,
        }
        for version in [None, 0]
    ] + [{"username": users[0].username, "role": roles[1].role, "version": 0}]

    for test in tests:
        consent = TosConsent.get(**test)
        assert consent is None
