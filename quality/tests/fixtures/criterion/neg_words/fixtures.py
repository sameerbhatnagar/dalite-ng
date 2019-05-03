import pytest

from .generators import (
    add_neg_words_criterion,
    add_neg_words_rules,
    new_neg_words_criterion,
    new_neg_words_rules,
)


@pytest.fixture
def neg_words_criterion():
    return add_neg_words_criterion(new_neg_words_criterion(1))[0]


@pytest.fixture
def neg_words_rules():
    return add_neg_words_rules(new_neg_words_rules(1))[0]
