import pytest

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinCharsCriterion
from quality.models.criterion.criterion import CriterionExistsError
from quality.tests.fixtures import *  # noqa


def test_evaluate__less_than_min(min_chars_criterion, answers):
    answer = answers[0]
    answer.rationale = ".."
    answer.save()

    min_chars_criterion.min_chars = 3
    min_chars_criterion.save()

    assert not min_chars_criterion.evaluate(answer)


def test_evaluate__more_than_min(min_chars_criterion, answers):
    answer = answers[0]
    answer.rationale = "...."
    answer.save()

    min_chars_criterion.min_chars = 3
    min_chars_criterion.save()

    assert min_chars_criterion.evaluate(answer)


def test_evaluate__same_as_min(min_chars_criterion, answers):
    answer = answers[0]
    answer.rationale = "..."
    answer.save()

    min_chars_criterion.min_chars = 3
    min_chars_criterion.save()

    assert min_chars_criterion.evaluate(answer)


def test_create():
    min_chars = 5

    criterion = MinCharsCriterion.create(min_chars)
    assert criterion.name == "min_chars"
    assert criterion.min_chars == min_chars


def test_create__wrong_args():
    min_chars = -1

    with pytest.raises(ValueError):
        criterion = MinCharsCriterion.create(min_chars)


def test_create__already_exists(min_chars_criterion):
    with pytest.raises(CriterionExistsError):
        MinCharsCriterion.create(min_chars_criterion.min_chars)


def test_info():
    info = MinCharsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info
