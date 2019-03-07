import pytest

from quality.models.criterion import MinWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_create():
    min_words = 5

    criterion = MinWordsCriterionRules.create(min_words)
    assert criterion.min_words == min_words


def test_create__wrong_args():
    min_words = -1

    with pytest.raises(ValueError):
        criterion = MinWordsCriterionRules.create(min_words)


def test_dict(min_words_rules):
    min_words_rules.min_words = 3
    min_words_rules.save()

    data = dict(min_words_rules)
    assert data["min_words"] == 3
