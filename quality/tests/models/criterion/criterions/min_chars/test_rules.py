import pytest

from quality.models.criterion import MinCharsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_get_or_create__create():
    min_chars = 5

    criterion = MinCharsCriterionRules.get_or_create(min_chars)
    assert criterion.min_chars == min_chars


def test_get_or_create__create(min_chars_rules):
    min_chars = min_chars_rules.min_chars
    n_rules = MinCharsCriterionRules.objects.count()

    criterion = MinCharsCriterionRules.get_or_create(min_chars)
    assert criterion.min_chars == min_chars
    assert MinCharsCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    min_chars = -1

    with pytest.raises(ValueError):
        criterion = MinCharsCriterionRules.get_or_create(min_chars)


def test_dict(min_chars_rules):
    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    data = dict(min_chars_rules)
    assert len(data) == 1
    assert data["min_chars"]["name"] == "min_chars"
    assert data["min_chars"]["full_name"] == "Min characters"
    assert (
        data["min_chars"]["description"]
        == "The minimum number of characters needed by a rationale."
    )
    assert data["min_chars"]["value"] == 3
    assert data["min_chars"]["type"] == "PositiveIntegerField"
    assert len(data["min_chars"]) == 5
