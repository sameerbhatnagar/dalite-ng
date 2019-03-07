import pytest

from .generators import (
    add_min_words_criterion,
    add_min_words_rules,
    new_min_words_criterion,
    new_min_words_rules,
)


@pytest.fixture
def min_words_criterion():
    return add_min_words_criterion(new_min_words_criterion(1))[0]


@pytest.fixture
def min_words_rules():
    return add_min_words_rules(new_min_words_rules(1))[0]
