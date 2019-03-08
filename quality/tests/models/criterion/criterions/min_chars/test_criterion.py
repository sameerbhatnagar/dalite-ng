from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinCharsCriterion, MinCharsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_info():
    info = MinCharsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_evaluate__less_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    answer = answers[0]
    answer.rationale = ".."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert not min_chars_criterion.evaluate(answer, min_chars_rules.pk)


def test_evaluate__more_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    answer = answers[0]
    answer.rationale = "...."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)


def test_evaluate__same_as_min(min_chars_criterion, min_chars_rules, answers):
    answer = answers[0]
    answer.rationale = "..."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)


def test_evaluate__default(min_chars_criterion, answers):
    answer = answers[0]
    answer.rationale = ""
    answer.save()

    min_chars_rules = MinCharsCriterionRules.get_or_create()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)


def test_dict(min_chars_criterion):
    data = dict(min_chars_criterion)
    assert "version" in data
    assert "is_beta" in data
    assert len(data) == 2
