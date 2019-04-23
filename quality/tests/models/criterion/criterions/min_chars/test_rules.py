import pytest

from quality.models.criterion import MinCharsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_str(min_chars_rules):
    assert str(min_chars_rules) == "Rules {} for criterion min_chars".format(
        min_chars_rules.pk
    )


def test_get_or_create__create():
    min_chars = 5

    criterion = MinCharsCriterionRules.get_or_create(min_chars=min_chars)
    assert criterion.min_chars == min_chars


def test_get_or_create__get(min_chars_rules):
    min_chars = min_chars_rules.min_chars
    threshold = min_chars_rules.threshold
    n_rules = MinCharsCriterionRules.objects.count()

    criterion = MinCharsCriterionRules.get_or_create(
        threshold=threshold, min_chars=min_chars
    )
    assert criterion.min_chars == min_chars
    assert MinCharsCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    min_chars = -1
    with pytest.raises(ValueError):
        criterion = MinCharsCriterionRules.get_or_create(min_chars=min_chars)

    threshold = 2
    with pytest.raises(ValueError):
        criterion = MinCharsCriterionRules.get_or_create(threshold=threshold)


def test_dict(min_chars_rules):
    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    data = dict(min_chars_rules)
    assert len(data) == 2
    assert data["threshold"]["name"] == "threshold"
    assert data["threshold"]["full_name"] == "Threshold"
    assert (
        data["threshold"]["description"]
        == "Minimum value for the answer to be accepted"
    )
    assert data["threshold"]["value"] == 1
    assert data["threshold"]["type"] == "ProbabilityField"
    assert data["threshold"]["allowed"] is None
    assert len(data["threshold"]) == 6
    assert data["min_chars"]["name"] == "min_chars"
    assert data["min_chars"]["full_name"] == "Min characters"
    assert (
        data["min_chars"]["description"]
        == "The minimum number of characters needed by a rationale."
    )
    assert data["min_chars"]["value"] == 3
    assert data["min_chars"]["type"] == "PositiveIntegerField"
    assert data["min_chars"]["allowed"] is None
    assert len(data["min_chars"]) == 6
