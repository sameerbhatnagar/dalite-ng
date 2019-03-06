import pytest

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinWordsCriterion
from quality.models.criterion.criterion import CriterionExistsError
from quality.tests.fixtures import *  # noqa


def test_evaluate__less_than_min(min_words_criterion, answers):
    answer = answers[0]
    answer.rationale = ". ."
    answer.save()

    min_words_criterion.min_words = 3
    min_words_criterion.save()

    assert not min_words_criterion.evaluate(answer)


def test_evaluate__more_than_min(min_words_criterion, answers):
    answer = answers[0]
    answer.rationale = ". . . ."
    answer.save()

    min_words_criterion.min_words = 3
    min_words_criterion.save()

    assert min_words_criterion.evaluate(answer)


def test_evaluate__same_as_min(min_words_criterion, answers):
    answer = answers[0]
    answer.rationale = ". . ."
    answer.save()

    min_words_criterion.min_words = 3
    min_words_criterion.save()

    assert min_words_criterion.evaluate(answer)


def test_create():
    min_words = 5

    criterion = MinWordsCriterion.create(min_words)
    assert criterion.name == "min_words"
    assert criterion.min_words == min_words


def test_create__wrong_args():
    min_words = -1

    with pytest.raises(ValueError):
        criterion = MinWordsCriterion.create(min_words)


def test_create__already_exists(min_words_criterion):
    with pytest.raises(CriterionExistsError):
        MinWordsCriterion.create(min_words_criterion.min_words)


def test_info():
    info = MinWordsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info
