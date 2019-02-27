import pytest

from .generators import add_min_words_criterion, new_min_words_criterion


@pytest.fixture
def min_words_criterion():
    return add_min_words_criterion(new_min_words_criterion(1))[0]
