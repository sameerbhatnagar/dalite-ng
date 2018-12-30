import pytest
from .generators import add_tos, add_tos_consents, new_tos, new_tos_consents


@pytest.fixture
def tos_student():
    return add_tos(new_tos(1, "student"))[0]


@pytest.fixture
def tos_teacher():
    return add_tos(new_tos(1, "teacher"))[0]
