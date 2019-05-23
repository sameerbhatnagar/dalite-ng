import pytest

from .generators import (
    add_min_chars_criterion,
    add_min_chars_rules,
    new_min_chars_criterion,
    new_min_chars_rules,
)


@pytest.fixture
def min_chars_criterion():
    return add_min_chars_criterion(new_min_chars_criterion(1))[0]


@pytest.fixture
def min_chars_rules():
    return add_min_chars_rules(new_min_chars_rules(1))[0]
