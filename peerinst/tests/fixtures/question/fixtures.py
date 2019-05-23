import pytest

from .generators import (
    add_questions,
    add_rationale_only_questions,
    new_questions,
)


@pytest.fixture
def question():
    return add_questions(new_questions(1))[0]


@pytest.fixture
def questions():
    return add_questions(new_questions(2))


@pytest.fixture
def rationale_only_question():
    return add_rationale_only_questions(new_questions(1))[0]


@pytest.fixture
def rationale_only_questions():
    return add_rationale_only_questions(new_questions(2))
