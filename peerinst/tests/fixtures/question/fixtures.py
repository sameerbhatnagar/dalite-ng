import pytest

from ..teacher import teacher  # noqa
from .generators import (
    add_questions,
    add_rationale_only_questions,
    new_questions,
)


@pytest.fixture
def question(teacher):
    return add_questions(new_questions(1, teacher))[0]


@pytest.fixture
def questions(teacher):
    return add_questions(new_questions(10, teacher))


@pytest.fixture
def rationale_only_question():
    return add_rationale_only_questions(new_questions(1))[0]


@pytest.fixture
def rationale_only_questions():
    return add_rationale_only_questions(new_questions(2))
