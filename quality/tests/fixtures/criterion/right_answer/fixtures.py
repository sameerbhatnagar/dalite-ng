import pytest

from .generators import (
    add_right_answer_criterion,
    add_right_answer_rules,
    new_right_answer_criterion,
    new_right_answer_rules,
)


@pytest.fixture
def right_answer_criterion():
    return add_right_answer_criterion(new_right_answer_criterion(1))[0]


@pytest.fixture
def right_answer_rules():
    return add_right_answer_rules(new_right_answer_rules(1))[0]
