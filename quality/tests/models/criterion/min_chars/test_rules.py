import pytest

from quality.models.criterion import MinCharsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_create():
    min_chars = 5

    criterion = MinCharsCriterionRules.create(min_chars)
    assert criterion.min_chars == min_chars


def test_create__wrong_args():
    min_chars = -1

    with pytest.raises(ValueError):
        criterion = MinCharsCriterionRules.create(min_chars)


def test_dict(min_chars_rules):
    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    data = dict(min_chars_rules)
    assert data["min_chars"] == 3
