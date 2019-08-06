import pytest

from . import factories as f


@pytest.fixture
def new_user():
    return f.UserFactory()


@pytest.fixture
def inactive_user():
    return f.UserFactory(is_active=False)
