import pytest

from quality.models.criterion import MinWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_get_or_create__create():
    min_words = 5

    criterion = MinWordsCriterionRules.get_or_create(min_words)
    assert criterion.min_words == min_words


def test_get_or_create__get(min_words_rules):
    min_words = min_words_rules.min_words
    n_rules = MinWordsCriterionRules.objects.count()

    criterion = MinWordsCriterionRules.get_or_create(min_words)
    assert criterion.min_words == min_words
    assert MinWordsCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    min_words = -1

    with pytest.raises(ValueError):
        criterion = MinWordsCriterionRules.get_or_create(min_words)


def test_dict(min_words_rules):
    min_words_rules.min_words = 3
    min_words_rules.save()

    data = dict(min_words_rules)
    assert data["min_words"] == 3
    assert len(data) == 1
