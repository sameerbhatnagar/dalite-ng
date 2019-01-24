import pytest

from ..question import questions  # noqa
from .generators import add_assignments, new_assignments


@pytest.fixture
def assignment(questions):
    return add_assignments(
        new_assignments(1, questions, min_questions=len(questions))
    )[0]
