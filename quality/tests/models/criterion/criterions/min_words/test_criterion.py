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


def test_dict(min_words_criterion):
    data = dict(min_words_criterion)
    assert "name" in data
    assert "full_name" in data
    assert "description" in data
    assert "version" in data
    assert "versions" in data
    for version in data["versions"]:
        assert "version" in version
        assert "is_beta" in version
        assert len(version) == 2
    assert len(data) == 5
