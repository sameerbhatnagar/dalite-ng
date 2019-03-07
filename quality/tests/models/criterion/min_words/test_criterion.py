import mock

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinWordsCriterion, MinWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_info():
    info = MinWordsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_evaluate__less_than_min(
    min_words_criterion, min_words_rules, answers
):
    answer = answers[0]
    answer.rationale = ". ."
    answer.save()

    min_words_rules.min_words = 3
    min_words_rules.save()

    assert not min_words_criterion.evaluate(answer, min_words_rules.pk)


def test_evaluate__more_than_min(
    min_words_criterion, min_words_rules, answers
):
    answer = answers[0]
    answer.rationale = ". . . ."
    answer.save()

    min_words_rules.min_words = 3
    min_words_rules.save()

    assert min_words_criterion.evaluate(answer, min_words_rules.pk)


def test_evaluate__same_as_min(min_words_criterion, min_words_rules, answers):
    answer = answers[0]
    answer.rationale = ". . ."
    answer.save()

    min_words_rules.min_words = 3
    min_words_rules.save()

    assert min_words_criterion.evaluate(answer, min_words_rules.pk)


def test_evaluate__default(min_words_criterion, answers):
    answer = answers[0]
    answer.rationale = ""
    answer.save()

    min_words_rules = MinWordsCriterionRules.get_or_create()

    assert min_words_criterion.evaluate(answer, min_words_rules.pk)


def test_serialize(min_words_criterion):
    min_words_criterion.uses_rules = "a,b,c"
    min_words_criterion.save()

    with mock.patch(
        "quality.models.criterion.min_words.MinWordsCriterionRules.objects.get"
    ) as rules_get:
        rules_get.return_value = iter([("a", 1), ("b", 2), ("c", 3)])
        data = min_words_criterion.serialize(0)
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 3
        assert "version" in data
        assert "is_beta" in data


def test_serialize__subset_of_rules(min_words_criterion):
    min_words_criterion.uses_rules = "a,c"
    min_words_criterion.save()

    with mock.patch(
        "quality.models.criterion.min_words.MinWordsCriterionRules.objects.get"
    ) as rules_get:
        rules_get.return_value = iter([("a", 1), ("b", 2), ("c", 3)])
        data = min_words_criterion.serialize(0)
        assert data["a"] == 1
        assert data["c"] == 3
        assert "version" in data
        assert "is_beta" in data
        assert "b" not in data


def test_rules(min_words_criterion):
    min_words_criterion.uses_rules = "a,b,c,d"
    min_words_criterion.save()
    assert min_words_criterion.rules == ["a", "b", "c", "d"]

    min_words_criterion.uses_rules = "a, b, c, d"
    min_words_criterion.save()
    assert min_words_criterion.rules == ["a", "b", "c", "d"]

    min_words_criterion.uses_rules = "a , b , c , d"
    min_words_criterion.save()
    assert min_words_criterion.rules == ["a", "b", "c", "d"]
