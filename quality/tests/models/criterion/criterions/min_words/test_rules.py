import pytest

from quality.models.criterion import MinWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_str(min_words_rules):
    assert str(min_words_rules) == "Rules {} for criterion min_words".format(
        min_words_rules.pk
    )


def test_get_or_create__create():
    min_words = 5

    criterion = MinWordsCriterionRules.get_or_create(min_words=min_words)
    assert criterion.min_words == min_words


def test_get_or_create__get(min_words_rules):
    min_words = min_words_rules.min_words
    threshold = min_words_rules.threshold
    n_rules = MinWordsCriterionRules.objects.count()

    criterion = MinWordsCriterionRules.get_or_create(
        threshold=threshold, min_words=min_words
    )
    assert criterion.min_words == min_words
    assert MinWordsCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    min_words = -1
    with pytest.raises(ValueError):
        criterion = MinWordsCriterionRules.get_or_create(min_words=min_words)

    threshold = 2
    with pytest.raises(ValueError):
        criterion = MinWordsCriterionRules.get_or_create(threshold=threshold)


def test_dict(min_words_rules):
    min_words_rules.min_words = 3
    min_words_rules.save()

    data = dict(min_words_rules)
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
    assert data["min_words"]["name"] == "min_words"
    assert data["min_words"]["full_name"] == "Min words"
    assert (
        data["min_words"]["description"]
        == "The minimum number of words needed by a rationale."
    )
    assert data["min_words"]["value"] == 3
    assert data["min_words"]["type"] == "PositiveIntegerField"
    assert data["min_words"]["allowed"] is None
    assert len(data["min_words"]) == 6
