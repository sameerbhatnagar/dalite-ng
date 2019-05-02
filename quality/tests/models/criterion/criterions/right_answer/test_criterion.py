import pytest

from peerinst.tests.fixtures import *  # noqa
from quality.models.criterion import (
    RightAnswerCriterion,
    RightAnswerCriterionRules,
)
from quality.tests.fixtures import *  # noqa


def test_info():
    info = RightAnswerCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = RightAnswerCriterion.objects.count()
    criterion = RightAnswerCriterion.create_default()
    assert isinstance(criterion, RightAnswerCriterion)
    assert RightAnswerCriterion.objects.count() == n + 1


def test_evaluate__all_evaluated__right_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 1
    )


def test_evaluate__all_evaluated__right_first_wrong_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0.5
    )


def test_evaluate__all_evaluated__wrong_first_right_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0.5
    )


def test_evaluate__all_evaluated__wrong_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0
    )


def test_evaluate__only_last__right_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 1
    )


def test_evaluate__only_last__right_first_wrong_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0
    )


def test_evaluate__only_last__wrong_first_right_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 1
    )


def test_evaluate__only_last__wrong_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0
    )


def test_evaluate__default__right_first_and_second__multiple_choice(
    right_answer_criterion, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 1
    )


def test_evaluate__default__right_first_wrong_second__multiple_choice(
    right_answer_criterion, answers
):
    answer = answers[0]
    answer.first_answer_choice = 1
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0.5
    )


def test_evaluate__default__wrong_first_right_second__multiple_choice(
    right_answer_criterion, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 1
    answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0.5
    )


def test_evaluate__default__wrong_first_and_second__multiple_choice(
    right_answer_criterion, answers
):
    answer = answers[0]
    answer.first_answer_choice = 2
    answer.second_answer_choice = 2
    answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    assert (
        right_answer_criterion.evaluate(answer, right_answer_rules.pk)[
            "quality"
        ]
        == 0
    )


def test_evaluate__wrong_argument(
    right_answer_criterion, right_answer_rules, answers
):
    answer = answers[0]

    with pytest.raises(ValueError):
        right_answer_criterion.evaluate(
            answer.rationale, right_answer_rules.pk
        )


def test_batch_evaluate__all_batch_evaluated__right_first_and_second__multiple_choice(  # noqa
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 1


def test_batch_evaluate__all_batch_evaluated__right_first_wrong_second__multiple_choice(  # noqa
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0.5


def test_batch_evaluate__all_batch_evaluated__wrong_first_right_second__multiple_choice(  # noqa
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0.5


def test_batch_evaluate__all_batch_evaluated__wrong_first_and_second__multiple_choice(  # noqa
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules.only_last = False
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0


def test_batch_evaluate__only_last__right_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 1


def test_batch_evaluate__only_last__right_first_wrong_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0


def test_batch_evaluate__only_last__wrong_first_right_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 1


def test_batch_evaluate__only_last__wrong_first_and_second__multiple_choice(
    right_answer_criterion, right_answer_rules, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules.only_last = True
    right_answer_rules.save()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0


def test_batch_evaluate__default__right_first_and_second__multiple_choice(
    right_answer_criterion, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 1


def test_batch_evaluate__default__right_first_wrong_second__multiple_choice(
    right_answer_criterion, answers
):
    for answer in answers:
        answer.first_answer_choice = 1
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0.5


def test_batch_evaluate__default__wrong_first_right_second__multiple_choice(
    right_answer_criterion, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 1
        answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0.5


def test_batch_evaluate__default__wrong_first_and_second__multiple_choice(
    right_answer_criterion, answers
):
    for answer in answers:
        answer.first_answer_choice = 2
        answer.second_answer_choice = 2
        answer.save()

    right_answer_rules = RightAnswerCriterionRules.get_or_create()

    for quality in right_answer_criterion.batch_evaluate(
        answers, right_answer_rules.pk
    ):
        assert quality["quality"] == 0


def test_batch_evaluate__wrong_argument(
    right_answer_criterion, right_answer_rules, answers
):
    with pytest.raises(ValueError):
        right_answer_criterion.batch_evaluate(
            [answer.rationale for answer in answers], right_answer_rules.pk
        )


def test_rules(right_answer_criterion):
    right_answer_criterion.uses_rules = []
    right_answer_criterion.save()
    assert right_answer_criterion.rules == []


def test_dict(right_answer_criterion):
    data = dict(right_answer_criterion)
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
