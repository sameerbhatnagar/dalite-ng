import mock

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinCharsCriterion
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


def test_serialize(min_chars_criterion):
    min_chars_criterion.uses_rules = "a,b,c"
    min_chars_criterion.save()

    with mock.patch(
        "quality.models.criterion.min_chars.MinCharsCriterionRules.objects.get"
    ) as rules_get:
        rules_get.return_value = iter([("a", 1), ("b", 2), ("c", 3)])
        data = min_chars_criterion.serialize(0)
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 3
        assert "version" in data
        assert "is_beta" in data


def test_serialize__subset_of_rules(min_chars_criterion):
    min_chars_criterion.uses_rules = "a,c"
    min_chars_criterion.save()

    with mock.patch(
        "quality.models.criterion.min_chars.MinCharsCriterionRules.objects.get"
    ) as rules_get:
        rules_get.return_value = iter([("a", 1), ("b", 2), ("c", 3)])
        data = min_chars_criterion.serialize(0)
        assert data["a"] == 1
        assert data["c"] == 3
        assert "version" in data
        assert "is_beta" in data
        assert "b" not in data


def test_rules(min_chars_criterion):
    min_chars_criterion.uses_rules = "a,b,c,d"
    min_chars_criterion.save()
    assert min_chars_criterion.rules == ["a", "b", "c", "d"]

    min_chars_criterion.uses_rules = "a, b, c, d"
    min_chars_criterion.save()
    assert min_chars_criterion.rules == ["a", "b", "c", "d"]

    min_chars_criterion.uses_rules = "a , b , c , d"
    min_chars_criterion.save()
    assert min_chars_criterion.rules == ["a", "b", "c", "d"]
