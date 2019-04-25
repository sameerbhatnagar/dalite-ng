# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string
import time

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import (
    LikelihoodCriterion,
    LikelihoodCriterionRules,
)
from quality.tests.fixtures import *  # noqa


def test_info():
    info = LikelihoodCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = LikelihoodCriterion.objects.count()
    criterion = LikelihoodCriterion.create_default()
    assert isinstance(criterion, LikelihoodCriterion)
    assert LikelihoodCriterion.objects.count() == n + 1


def test_evaluate__english_french__english(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "All happy families are alike; each unhappy family is unhappy in its "
        "own way."
    )
    answer.save()

    likelihood_rules.languages = ["english", "french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__english_french__french(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "Les familles heureuses se ressemblent toutes; les familles "
        "malheureuses sont malheureuses chacune à leur façon."
    )
    answer.save()

    likelihood_rules.languages = ["english", "french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__english_french__random(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = "".join(
        random.choice([" "] + list(string.ascii_letters))
        for _ in range(random.randint(5, 50))
    )
    answer.save()

    likelihood_rules.languages = ["english", "french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_evaluate__english__english(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "All happy families are alike; each unhappy family is unhappy in its "
        "own way."
    )
    answer.save()

    likelihood_rules.languages = ["english"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__english__french(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "Les familles heureuses se ressemblent toutes; les familles "
        "malheureuses sont malheureuses chacune à leur façon."
    )
    answer.save()

    likelihood_rules.languages = ["english"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_evaluate__english__random(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = "".join(
        random.choice([" "] + list(string.ascii_letters))
        for _ in range(random.randint(5, 50))
    )
    answer.save()

    likelihood_rules.languages = ["english"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_evaluate__french__english(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "All happy families are alike; each unhappy family is unhappy in its "
        "own way."
    )
    answer.save()

    likelihood_rules.languages = ["french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_evaluate__french__french(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = (
        "Les familles heureuses se ressemblent toutes; les familles "
        "malheureuses sont malheureuses chacune à leur façon."
    )
    answer.save()

    likelihood_rules.languages = ["french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__french__random(
    likelihood_criterion, likelihood_rules, answers
):
    answer = answers[0]
    answer.rationale = "".join(
        random.choice([" "] + list(string.ascii_letters))
        for _ in range(random.randint(5, 50))
    )
    answer.save()

    likelihood_rules.languages = ["french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_evaluate__default__english(likelihood_criterion, answers):
    answer = answers[0]
    answer.rationale = (
        "All happy families are alike; each unhappy family is unhappy in its "
        "own way."
    )
    answer.save()

    likelihood_rules = LikelihoodCriterionRules.get_or_create()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__default__french(likelihood_criterion, answers):
    answer = answers[0]
    answer.rationale = (
        "Les familles heureuses se ressemblent toutes; les familles "
        "malheureuses sont malheureuses chacune à leur façon."
    )
    answer.save()

    likelihood_rules = LikelihoodCriterionRules.get_or_create()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        >= 0.95
    )


def test_evaluate__default__random(likelihood_criterion, answers):
    answer = answers[0]
    answer.rationale = "".join(
        random.choice([" "] + list(string.ascii_letters))
        for _ in range(random.randint(5, 50))
    )
    answer.save()

    likelihood_rules = LikelihoodCriterionRules.get_or_create()

    assert (
        likelihood_criterion.evaluate(answer, likelihood_rules.pk)["quality"]
        < 0.95
    )


def test_rules(likelihood_criterion):
    likelihood_criterion.uses_rules = ["a", "b", "c", "d"]
    likelihood_criterion.save()
    assert likelihood_criterion.rules == ["a", "b", "c", "d"]


def test_dict(likelihood_criterion):
    data = dict(likelihood_criterion)
    assert "name" in data
    assert "full_name" in data
    assert "description" in data
    assert "version" in data
    assert "versions" in data
    for version in data["versions"]:
        assert "version" in version
        assert "is_beta" in version
        assert "binary_threshold" in version
        assert len(version) == 3
    assert len(data) == 5


def test_cache(likelihood_criterion, likelihood_rules, answers):
    answer = answers[0]
    answer.rationale = (
        "All happy families are alike; each unhappy family is unhappy in its "
        "own way."
    )
    answer.save()

    likelihood_rules.languages = ["english", "french"]
    likelihood_rules.max_gram = 3
    likelihood_rules.save()

    start = time.time()
    quality_1 = likelihood_criterion.evaluate(answer, likelihood_rules.pk)[
        "quality"
    ]
    time_taken_1 = time.time() - start

    start = time.time()
    quality_2 = likelihood_criterion.evaluate(answer, likelihood_rules.pk)[
        "quality"
    ]
    time_taken_2 = time.time() - start

    assert quality_1 == quality_2
    assert time_taken_2 < time_taken_1
