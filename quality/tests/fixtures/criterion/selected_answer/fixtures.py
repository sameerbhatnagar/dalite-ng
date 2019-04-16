import pytest

from .generators import (
    add_selected_answer_criterion,
    add_selected_answer_rules,
    new_selected_answer_criterion,
    new_selected_answer_rules,
)


@pytest.fixture
def selected_answer_criterion():
    return add_selected_answer_criterion(new_selected_answer_criterion(1))[0]


@pytest.fixture
def selected_answer_rules():
    return add_selected_answer_rules(new_selected_answer_rules(1))[0]
