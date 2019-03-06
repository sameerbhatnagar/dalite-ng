import pytest

from .generators import (
    add_min_chars_criterion,
    add_min_words_criterion,
    new_min_chars_criterion,
    new_min_words_criterion,
)


@pytest.fixture
def min_words_criterion():
    return add_min_words_criterion(new_min_words_criterion(1))[0]


@pytest.fixture
def min_chars_criterion():
    return add_min_chars_criterion(new_min_chars_criterion(1))[0]
