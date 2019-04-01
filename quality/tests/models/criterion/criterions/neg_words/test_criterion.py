from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import NegWordsCriterion, NegWordsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_info():
    info = NegWordsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = NegWordsCriterion.objects.count()
    criterion = NegWordsCriterion.create_default()
    assert isinstance(criterion, NegWordsCriterion)
    assert NegWordsCriterion.objects.count() == n + 1


def test_evaluate__no_neg_words(neg_words_criterion, neg_words_rules, answers):
    answer = answers[0]
    answer.rationale = "a b c"
    answer.save()

    neg_words_rules.neg_words = []
    neg_words_rules.save()

    assert (
        neg_words_criterion.evaluate(answer, neg_words_rules.pk)["quality"]
        == 1
    )


def test_evaluate__no_neg_words_present(
    neg_words_criterion, neg_words_rules, answers
):
    answer = answers[0]
    answer.rationale = "a b c"
    answer.save()

    neg_words_rules.neg_words = ["d"]
    neg_words_rules.save()

    assert (
        neg_words_criterion.evaluate(answer, neg_words_rules.pk)["quality"]
        == 1
    )


def test_evaluate__all_neg_words_present(
    neg_words_criterion, neg_words_rules, answers
):
    answer = answers[0]
    answer.rationale = "a b c"
    answer.save()

    neg_words_rules.neg_words = ["a", "b", "c"]
    neg_words_rules.save()

    assert not neg_words_criterion.evaluate(answer, neg_words_rules.pk)[
        "quality"
    ]


def test_evaluate__some_neg_words_present(
    neg_words_criterion, neg_words_rules, answers
):
    answer = answers[0]
    answer.rationale = "a b c"
    answer.save()

    neg_words_rules.neg_words = ["a", "b"]
    neg_words_rules.save()

    assert (
        neg_words_criterion.evaluate(answer, neg_words_rules.pk)["quality"] < 1
    )


def test_evaluate__default(neg_words_criterion, answers):
    answer = answers[0]
    answer.rationale = ""
    answer.save()

    neg_words_rules = NegWordsCriterionRules.get_or_create()

    assert (
        neg_words_criterion.evaluate(answer, neg_words_rules.pk)["quality"]
        == 1
    )


def test_rules(neg_words_criterion):
    neg_words_criterion.uses_rules = ["a", "b", "c", "d"]
    neg_words_criterion.save()
    assert neg_words_criterion.rules == ["a", "b", "c", "d"]


def test_dict(neg_words_criterion):
    data = dict(neg_words_criterion)
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
