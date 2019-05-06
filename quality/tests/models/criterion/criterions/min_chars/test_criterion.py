from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import MinCharsCriterion, MinCharsCriterionRules
from quality.tests.fixtures import *  # noqa


def test_info():
    info = MinCharsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = MinCharsCriterion.objects.count()
    criterion = MinCharsCriterion.create_default()
    assert isinstance(criterion, MinCharsCriterion)
    assert MinCharsCriterion.objects.count() == n + 1


def test_evaluate__less_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    answer = answers[0]
    answer.rationale = ".."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert not min_chars_criterion.evaluate(answer, min_chars_rules.pk)[
        "quality"
    ]


def test_evaluate__more_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    answer = answers[0]
    answer.rationale = "...."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)["quality"]


def test_evaluate__same_as_min(min_chars_criterion, min_chars_rules, answers):
    answer = answers[0]
    answer.rationale = "..."
    answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)["quality"]


def test_evaluate__default(min_chars_criterion, answers):
    answer = answers[0]
    answer.rationale = ""
    answer.save()

    min_chars_rules = MinCharsCriterionRules.get_or_create()

    assert min_chars_criterion.evaluate(answer, min_chars_rules.pk)["quality"]


def test_batch_evaluate__less_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    for answer in answers:
        answer.rationale = ".."
        answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    for quality in min_chars_criterion.batch_evaluate(
        answers, min_chars_rules.pk
    ):
        assert not quality["quality"]


def test_batch_evaluate__more_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    for answer in answers:
        answer.rationale = "...."
        answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    for quality in min_chars_criterion.batch_evaluate(
        answers, min_chars_rules.pk
    ):
        assert quality["quality"]


def test_batch_evaluate__same_than_min(
    min_chars_criterion, min_chars_rules, answers
):
    for answer in answers:
        answer.rationale = "..."
        answer.save()

    min_chars_rules.min_chars = 3
    min_chars_rules.save()

    for quality in min_chars_criterion.batch_evaluate(
        answers, min_chars_rules.pk
    ):
        assert quality["quality"]


def test_batch_evaluate__default(min_chars_criterion, answers):
    for answer in answers:
        answer.rationale = ""
        answer.save()

    min_chars_rules = MinCharsCriterionRules.get_or_create()

    for quality in min_chars_criterion.batch_evaluate(
        answers, min_chars_rules.pk
    ):
        assert quality["quality"]


def test_rules(min_chars_criterion):
    min_chars_criterion.uses_rules = ["a", "b", "c", "d"]
    min_chars_criterion.save()
    assert min_chars_criterion.rules == ["a", "b", "c", "d"]


def test_dict(min_chars_criterion):
    data = dict(min_chars_criterion)
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
