import pytest

from quality.models.criterion import LikelihoodCriterionRules
from quality.tests.fixtures import *  # noqa


def test_str(likelihood_rules):
    assert str(likelihood_rules) == "Rules {} for criterion likelihood".format(
        likelihood_rules.pk
    )


def test_get_or_create__create():
    languages = ["english"]
    max_gram = 1

    criterion = LikelihoodCriterionRules.get_or_create(
        languages=languages, max_gram=max_gram
    )
    assert criterion.languages == languages
    assert criterion.max_gram == max_gram


def test_get_or_create__get(likelihood_rules):
    languages = likelihood_rules.languages
    max_gram = likelihood_rules.max_gram
    threshold = likelihood_rules.threshold
    n_rules = LikelihoodCriterionRules.objects.count()

    criterion = LikelihoodCriterionRules.get_or_create(
        threshold=threshold, languages=languages, max_gram=max_gram
    )
    assert criterion.languages == languages
    assert criterion.max_gram == max_gram
    assert LikelihoodCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    languages = "english"
    with pytest.raises(ValueError):
        criterion = LikelihoodCriterionRules.get_or_create(languages=languages)

    max_gram = 0
    with pytest.raises(ValueError):
        criterion = LikelihoodCriterionRules.get_or_create(max_gram=max_gram)

    threshold = 2
    with pytest.raises(ValueError):
        criterion = LikelihoodCriterionRules.get_or_create(threshold=threshold)


def test_dict(likelihood_rules):
    likelihood_rules.languages = ["english"]
    likelihood_rules.max_gram = 2
    likelihood_rules.save()

    data = dict(likelihood_rules)
    assert len(data) == 3
    assert data["threshold"]["name"] == "threshold"
    assert data["threshold"]["full_name"] == "Threshold"
    assert (
        data["threshold"]["description"]
        == "Minimum value for the answer to be accepted"
    )
    assert data["threshold"]["value"] == 1
    assert data["threshold"]["type"] == "ProbabilityField"
    assert len(data["threshold"]) == 5
    assert data["languages"]["name"] == "languages"
    assert data["languages"]["full_name"] == "Languages"
    assert (
        data["languages"]["description"]
        == "Accepted languages. Choices are english and french."
    )
    assert data["languages"]["value"] == ["english"]
    assert data["languages"]["type"] == "CommaSepField"
    assert len(data["languages"]) == 5
    assert data["max_gram"]["name"] == "max_gram"
    assert data["max_gram"]["full_name"] == "Max gram"
    assert (
        data["max_gram"]["description"] == "The maximum size of n-gram to use."
    )
    assert data["max_gram"]["value"] == 2
    assert data["max_gram"]["type"] == "PositiveIntegerField"
    assert len(data["max_gram"]) == 5
