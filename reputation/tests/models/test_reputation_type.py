# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest

from peerinst.tests.fixtures import *  # noqa
from reputation.models import ReputationType, UsesCriterion
from reputation.tests.fixtures import *  # noqa


def test_str(question_reputation, assignment_reputation, teacher_reputation):
    assert str(question_reputation.reputation_type) == "question"
    assert str(assignment_reputation.reputation_type) == "assignment"
    assert str(teacher_reputation.reputation_type) == "teacher"


def test_calculate_points__no_threshold(question_reputation):
    reputation_type = question_reputation.reputation_type

    criterion = mock.Mock()
    model = mock.Mock()
    criterion.evaluate.return_value = 50
    criterion.thresholds = []
    criterion.points_per_threshold = ["2"]

    assert reputation_type._calculate_points(criterion, model) == 100


def test_calculate_points__threshold_same__as_points(question_reputation):
    reputation_type = question_reputation.reputation_type

    criterion = mock.Mock()
    model = mock.Mock()
    criterion.evaluate.return_value = 50
    criterion.thresholds = ["10", "20", "30", "40"]
    criterion.points_per_threshold = ["4", "3", "2", "1"]

    assert reputation_type._calculate_points(criterion, model) == 10 * (
        4 + 3 + 2 + 1
    )


def test_calculate_points__threshold_less_than_points(question_reputation):
    reputation_type = question_reputation.reputation_type

    criterion = mock.Mock()
    model = mock.Mock()
    criterion.evaluate.return_value = 50
    criterion.thresholds = ["10", "20", "30", "40"]
    criterion.points_per_threshold = ["5", "4", "3", "2", "1"]

    assert reputation_type._calculate_points(criterion, model) == 10 * (
        5 + 4 + 3 + 2 + 1
    )


def test_evaluate(question_reputation):
    for i in range(3):
        UsesCriterion.objects.create(
            reputation_type=question_reputation.reputation_type,
            name="fake_{}".format(i + 1),
            version=1,
        )

    with mock.patch(
        "reputation.models.reputation_type.get_criterion"
    ) as get_criterion, mock.patch.object(
        ReputationType, "_calculate_points"
    ) as calculate_points:
        criterion_class = mock.Mock()
        get_criterion.return_value = criterion_class

        criterion = mock.MagicMock()
        criterion.__iter__.side_effect = {}.__iter__
        calculate_points.return_value = 1

        criterion_class.objects.get.return_value = criterion

        reputation, reputations = question_reputation.evaluate()

        assert reputation == 3
        for i, q in enumerate(reputations):
            assert q["reputation"] == 1


def test_evaluate__wrong_model(question_reputation, assignment_reputation):
    reputation_type = question_reputation.reputation_type
    with pytest.raises(TypeError):
        reputation_type.evaluate(assignment_reputation.reputation_model)


def test_evaluate__no_criterion(question_reputation):
    model = question_reputation.reputation_model
    reputation_type = question_reputation.reputation_type
    reputation, criteria = reputation_type.evaluate(model)
    assert reputation is None
    assert criteria == []
