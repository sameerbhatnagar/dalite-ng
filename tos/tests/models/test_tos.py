from datetime import datetime

import pytest
import pytz
from django.db import IntegrityError

from tos.models import Tos, _compute_hash

from ..fixtures import *  # noqa
from ..generators import new_tos


def test_new_tos(roles):
    n = 4
    data = new_tos(n, roles, all_roles_present=True, random_current=True)

    first_for_role = {role: True for role in roles}

    for d in data:
        time = datetime.now(pytz.utc)
        tos = Tos.objects.create(**d)
        assert isinstance(tos, Tos)
        assert tos.role == d["role"]
        assert tos.version == d["version"]
        assert tos.text == d["text"]
        if first_for_role[d["role"]]:
            assert tos.current
            first_for_role[d["role"]] = False
        else:
            assert tos.current == d["current"]
        assert tos.hash == _compute_hash(d["text"])
        assert tos.created > time
        assert tos.created < datetime.now(pytz.utc)


def test_new_tos__version_exists(roles):
    data = new_tos(2, roles=roles[0]) + new_tos(1, roles=roles[1])
    data[1]["version"] = data[0]["version"]
    data[2]["version"] = data[0]["version"]

    Tos.objects.create(**data[0])
    Tos.objects.create(**data[2])
    with pytest.raises(IntegrityError):
        Tos.objects.create(**data[1])


def test_new_tos_hash_exists(roles):
    data = new_tos(2, roles=roles[0]) + new_tos(1, roles=roles[1])
    data[1]["text"] = data[0]["text"]
    data[2]["text"] = data[0]["text"]

    Tos.objects.create(**data[0])
    Tos.objects.create(**data[2])
    with pytest.raises(IntegrityError):
        Tos.objects.create(**data[1])


def test_get_tos(toss_multiple_roles, roles):
    tests = [
        {"role": role.role, "version": version}
        for role in roles
        for version in [None, 0]
    ]

    for test in tests:
        tos, err = Tos.get(**test)
        assert isinstance(tos, Tos)
        assert err is None
        if test["version"] is None:
            correct = [
                t
                for t in toss_multiple_roles
                if t.role.role == test["role"] and t.current
            ][0]
        else:
            correct = [
                t
                for t in toss_multiple_roles
                if t.role.role == test["role"] and t.version == test["version"]
            ][0]
        assert tos.version == correct.version
        assert tos.role == correct.role
        assert tos.version == correct.version
        assert tos.hash == correct.hash
        assert tos.text == correct.text
        assert tos.created == correct.created


def test_get_tos__no_version(role):
    tests = [{"role": role.role, "version": None}]

    for test in tests:
        tos_, err = Tos.get(**test)
        assert tos_ is None
        assert err == (
            'No terms of service exist yet for role "{}".'.format(test["role"])
        )


def test_get_tos_version_doesnt_exist(tos):
    tests = [{"role": tos.role.role, "version": 1}]

    for test in tests:
        tos_, err = Tos.get(**test)
        assert tos_ is None
        assert err == (
            "There is no terms of service with version "
            '{} for role "{}"'.format(test["version"], test["role"])
        )
