import pytest

from quality.models.criterion import NegWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_str(neg_words_rules):
    assert str(neg_words_rules) == "Rules {} for criterion neg_words".format(
        neg_words_rules.pk
    )


def test_get_or_create__create():
    neg_words = ["a", "b", "c"]

    criterion = NegWordsCriterionRules.get_or_create(neg_words=neg_words)
    assert criterion.neg_words == neg_words


def test_get_or_create__get(neg_words_rules):
    neg_words = neg_words_rules.neg_words
    threshold = neg_words_rules.threshold
    n_rules = NegWordsCriterionRules.objects.count()

    criterion = NegWordsCriterionRules.get_or_create(
        threshold=threshold, neg_words=neg_words
    )
    assert criterion.neg_words == neg_words
    assert NegWordsCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    neg_words = 1
    with pytest.raises(ValueError):
        criterion = NegWordsCriterionRules.get_or_create(neg_words=neg_words)

    threshold = "a"
    with pytest.raises(TypeError):
        criterion = NegWordsCriterionRules.get_or_create(threshold=threshold)


def test_dict(neg_words_rules):
    neg_words_rules.neg_words = ["a", "b", "c"]
    neg_words_rules.save()

    data = dict(neg_words_rules)
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
    assert data["neg_words"]["name"] == "neg_words"
    assert data["neg_words"]["full_name"] == "Negative words"
    assert (
        data["neg_words"]["description"] == "Words considered to be negative."
    )
    assert data["neg_words"]["value"] == ["a", "b", "c"]
    assert data["neg_words"]["type"] == "CommaSepField"
    assert data["neg_words"]["allowed"] is None
    assert len(data["neg_words"]) == 6
