import pytest

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


@pytest.fixture
def user():
    return add_users(new_users(1))[0]


@pytest.fixture
def users():
    return add_users(new_users(2))


@pytest.fixture
def role():
    return add_roles(new_roles(1))[0]


@pytest.fixture
def roles():
    return add_roles(new_roles(2))


@pytest.fixture
def tos(role):
    return add_tos(new_tos(1, role, all_roles_present=False))[0]


@pytest.fixture
def toss_single_role(role):
    return add_tos(new_tos(2, role, all_roles_present=False))


@pytest.fixture
def toss_multiple_roles(roles):
    return add_tos(new_tos(4, roles, all_roles_present=True))


@pytest.fixture
def tos_consent(user, tos):
    return add_tos_consents(new_tos_consents(1, user, tos))[0]


@pytest.fixture
def tos_consents(users, toss_multiple_roles):
    return add_tos_consents(
        new_tos_consents(
            8, users, toss_multiple_roles, all_combinations_present=True
        )
    )


@pytest.fixture
def email_type(role):
    return add_email_types(new_email_types(1, role))


@pytest.fixture
def email_types(role):
    return add_email_types(new_email_types(2, role))


@pytest.fixture
def email_consents(email_types, users):
    return add_email_consents(
        new_email_consents(
            4, users, email_types, all_combinations_present=True
        )
    )
