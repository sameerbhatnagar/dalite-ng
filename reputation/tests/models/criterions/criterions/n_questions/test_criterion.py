# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from peerinst.tests.fixtures import *  # noqa
from reputation.models import NQuestionsCriterion, ReputationType
from reputation.tests.fixtures import *  # noqa


def test_dict(n_questions_criterion):
    data = dict(n_questions_criterion)
    assert "name" in data
    assert "full_name" in data
    assert "description" in data
    assert "version" in data
    assert len(data) == 4


def test_evaluate__wrong_model_type(n_questions_criterion, question):
    with pytest.raises(TypeError):
        n_questions_criterion.evaluate(question)

    n_questions_criterion.for_reputation_types.add(
        ReputationType.objects.get(type="question")
    )
    with pytest.raises(TypeError):
        n_questions_criterion.evaluate(question)


def test_evaluate__lower_than_floor(n_questions_criterion, teacher, questions):
    n_questions_criterion.floor = len(questions)
    n_questions_criterion.save()

    assert n_questions_criterion.evaluate(teacher) == 0


def test_evaluate__higher_than_ceiling(
    n_questions_criterion, teacher, questions
):
    n_questions_criterion.ceiling = len(questions)
    n_questions_criterion.save()

    assert n_questions_criterion.evaluate(teacher) == 1


def test_evaluate__between_floor_and_ceiling(
    n_questions_criterion, teacher, questions
):
    assert 0 < n_questions_criterion.evaluate(teacher) < 1


def test_info():
    info = NQuestionsCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info


def test_create_default():
    n = NQuestionsCriterion.objects.count()
    criterion = NQuestionsCriterion.create_default()
    assert isinstance(criterion, NQuestionsCriterion)
    assert NQuestionsCriterion.objects.count() == n + 1
