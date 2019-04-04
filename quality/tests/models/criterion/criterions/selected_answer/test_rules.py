import pytest

from quality.models.criterion import SelectedAnswerCriterionRules
from quality.tests.fixtures import *  # noqa


def test_str(selected_answer_rules):
    assert str(
        selected_answer_rules
    ) == "Rules {} for criterion selected_answer".format(
        selected_answer_rules.pk
    )


def test_get_or_create__create():
    default_if_never_shown = 1

    criterion = SelectedAnswerCriterionRules.get_or_create(
        default_if_never_shown=default_if_never_shown
    )
    assert criterion.default_if_never_shown == default_if_never_shown


def test_get_or_create__get(selected_answer_rules):
    default_if_never_shown = selected_answer_rules.default_if_never_shown
    threshold = selected_answer_rules.threshold
    n_rules = SelectedAnswerCriterionRules.objects.count()

    criterion = SelectedAnswerCriterionRules.get_or_create(
        threshold=threshold, default_if_never_shown=default_if_never_shown
    )
    assert criterion.default_if_never_shown == default_if_never_shown
    assert SelectedAnswerCriterionRules.objects.count() == n_rules


def test_get_or_create__wrong_args():
    threshold = 2
    with pytest.raises(ValueError):
        criterion = SelectedAnswerCriterionRules.get_or_create(
            threshold=threshold
        )

    default_if_never_shown = 2
    with pytest.raises(ValueError):
        criterion = SelectedAnswerCriterionRules.get_or_create(
            default_if_never_shown=default_if_never_shown
        )


def test_dict(selected_answer_rules):
    selected_answer_rules.default_if_never_shown = 1
    selected_answer_rules.save()

    data = dict(selected_answer_rules)
    assert len(data) == 2
    assert data["threshold"]["name"] == "threshold"
    assert data["threshold"]["full_name"] == "Threshold"
    assert (
        data["threshold"]["description"]
        == "Minimum value for the answer to be accepted"
    )
    assert data["threshold"]["value"] == 1
    assert data["threshold"]["type"] == "ProbabilityField"
    assert len(data["threshold"]) == 5
    assert data["default_if_never_shown"]["name"] == "default_if_never_shown"
    assert (
        data["default_if_never_shown"]["full_name"]
        == "Default value if never shown"
    )
    assert data["default_if_never_shown"]["description"] == (
        "Value to evaluate to if answer never shown before."
    )
    assert data["default_if_never_shown"]["value"] == 1
    assert data["default_if_never_shown"]["type"] == "ProbabilityField"
    assert len(data["default_if_never_shown"]) == 5
