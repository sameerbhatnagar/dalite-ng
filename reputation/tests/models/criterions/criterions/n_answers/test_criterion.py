# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from peerinst.tests.fixtures import *  # noqa
from reputation.models import NAnswersCriterion, ReputationType
from reputation.tests.fixtures import *  # noqa


def test_dict(n_answers_criterion):
    data = dict(n_answers_criterion)
    assert "name" in data
    assert "full_name" in data
    assert "description" in data
    assert "version" in data
    assert len(data) == 4


def test_evaluate__wrong_model_type(n_answers_criterion, teacher):
    with pytest.raises(TypeError):
        n_answers_criterion.evaluate(teacher)

    n_answers_criterion.for_reputation_types.add(
        ReputationType.objects.get(type="teacher")
    )
    with pytest.raises(TypeError):
        n_answers_criterion.evaluate(teacher)


def test_evaluate__lower_than_floor(n_answers_criterion, question, answers):
    n_answers_criterion.floor = len(answers)
    n_answers_criterion.save()

    assert n_answers_criterion.evaluate(question) == 0


def test_evaluate__higher_than_ceiling(n_answers_criterion, question, answers):
    n_answers_criterion.ceiling = len(answers)
    n_answers_criterion.save()

    assert n_answers_criterion.evaluate(question) == 1


def test_evaluate__between_floor_and_ceiling(
    n_answers_criterion, question, answers
):
    assert 0 < n_answers_criterion.evaluate(question) < 1


def test_info():
    info = NAnswersCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = NAnswersCriterion.objects.count()
    criterion = NAnswersCriterion.create_default()
    assert isinstance(criterion, NAnswersCriterion)
    assert NAnswersCriterion.objects.count() == n + 1
