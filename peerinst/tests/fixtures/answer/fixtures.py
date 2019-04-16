import pytest

from ..assignment import assignment  # noqa
from ..question import question  # noqa
from ..student import students  # noqa
from .generators import (
    add_answer_choices,
    add_answers_rationale_only,
    add_first_answers_no_shown,
    add_shown_and_second,
    new_answer_choice,
    new_answers_rationale_only,
    new_first_answers_no_shown,
)


@pytest.fixture
def answer_choices(question):
    return add_answer_choices(new_answer_choice(3, question))


@pytest.fixture
def answer_choice(question_rationale_only):
    return add_answer_choices(new_answer_choice(1, question))[0]


@pytest.fixture
def first_answers_no_shown(students, question, assignment, answer_choices):
    return add_first_answers_no_shown(
        new_first_answers_no_shown(
            len(students) * len(answer_choices),
            students,
            question,
            assignment,
            answer_choices,
        )
    )


@pytest.fixture
def answers(first_answers_no_shown):
    add_shown_and_second(first_answers_no_shown)
    return first_answers_no_shown


@pytest.fixture
def answers_rationale_only(student, question, assignment, answer_choice):
    return add_answers_rationale_only(
        new_answers_rationale_only(
            2, student, question, assignment, answer_choice
        )
    )
