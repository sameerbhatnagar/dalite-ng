# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from peerinst.tests.fixtures import *  # noqa
from reputation.models import NAnswersCriterion, ReputationType
from reputation.tests.fixtures import *  # noqa


def test_dict(n_answers_criterion):
    data = dict(n_answers_criterion)
    assert len(data) == 6
    assert "version" in data
    assert "points_per_threshold" in data
    assert "thresholds" in data
    assert "name" in data
    assert "full_name" in data
    assert "description" in data


def test_evaluate(n_answers_criterion, question, answers):
    assert n_answers_criterion.evaluate(question) == len(
        [a for a in answers if a.question == question]
    )


def test_evaluate__wrong_model_type(n_answers_criterion, teacher):
    with pytest.raises(TypeError):
        n_answers_criterion.evaluate(teacher)

    n_answers_criterion.for_reputation_types.add(
        ReputationType.objects.get(type="teacher")
    )
    with pytest.raises(TypeError):
        n_answers_criterion.evaluate(teacher)


def test_info():
    info = NAnswersCriterion.info()
    assert "name" in info
    assert "full_name" in info
    assert "description" in info
