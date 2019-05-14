# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest

from peerinst.tests.fixtures import *  # noqa
from reputation.models import UsesCriterion
from reputation.tests.fixtures import *  # noqa


def test_str(question_reputation, assignment_reputation, teacher_reputation):
    assert str(question_reputation.reputation_type) == "question"
    assert str(assignment_reputation.reputation_type) == "assignment"
    assert str(teacher_reputation.reputation_type) == "teacher"


def test_evaluate__wrong_model(question_reputation, assignment_reputation):
    reputation_type = question_reputation.reputation_type
    with pytest.raises(TypeError):
        reputation_type.evaluate(assignment_reputation.reputation_model)


def test_evaluate__no_criterion(question_reputation):
    model = question_reputation.reputation_model
    reputation_type = question_reputation.reputation_type
    reputation, criterions = reputation_type.evaluate(model)
    assert reputation is None
    assert criterions == []


def test_evaluate__all_equal(question_reputation):
    for i in range(3):
        UsesCriterion.objects.create(
            reputation_type=question_reputation.reputation_type,
            name="fake_{}".format(i + 1),
            version=1,
            weight=1,
        )

    with mock.patch(
        "reputation.models.reputation_type.get_criterion"
    ) as get_criterion:

        criterion_class = mock.Mock()
        get_criterion.return_value = criterion_class

        criterion = mock.MagicMock()
        criterion.__iter__.side_effect = {}.__iter__
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda model: next(evaluations)

        criterion_class.objects.get.return_value = criterion

        reputation, reputations = question_reputation.evaluate()

        assert reputation == (1.0 + 2 + 3) / 3
        for i, q in enumerate(reputations):
            assert q["reputation"] == i + 1
            assert q["weight"] == 1


def test_evaluate__different_weights(question_reputation):
    for i in range(3):
        UsesCriterion.objects.create(
            reputation_type=question_reputation.reputation_type,
            name="fake_{}".format(i + 1),
            version=1,
            weight=i + 1,
        )

    with mock.patch(
        "reputation.models.reputation_type.get_criterion"
    ) as get_criterion:

        criterion_class = mock.Mock()
        get_criterion.return_value = criterion_class

        criterion = mock.MagicMock()
        criterion.__iter__.side_effect = {}.__iter__
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda model: next(evaluations)

        criterion_class.objects.get.return_value = criterion

        reputation, reputations = question_reputation.evaluate()

        assert reputation == ((1.0 * 1 + 2 * 2 + 3 * 3) / (1 + 2 + 3))
        for i, q in enumerate(reputations):
            assert q["reputation"] == i + 1
            assert q["weight"] == i + 1
