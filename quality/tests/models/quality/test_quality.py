# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest

from quality.models import UsesCriterion
from quality.tests.fixtures import *  # noqa


def test_evaluate__no_criterions(assignment_quality):
    answer = mock.Mock()

    quality_, qualities = assignment_quality.evaluate(answer)

    assert quality_ is None
    assert qualities == []


def test_evaluate__all_equal(assignment_quality):
    answer = mock.Mock()

    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion_ = mock.Mock()
        criterion_.objects.count.return_value = 1
        get_criterion.return_value = {
            "criterion": criterion_,
            "rules": mock.Mock(),
        }
        criterion = mock.Mock()
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda answer, rules: next(evaluations)
        criterion_.objects.get.return_value = criterion
        for i in range(3):
            UsesCriterion.objects.create(
                quality=assignment_quality,
                name="fake_{}".format(i + 1),
                version=0,
                rules=0,
                weight=1,
            )

        quality_, qualities = assignment_quality.evaluate(answer)

        assert quality_ == (1.0 + 2 + 3) / 3
        for i, q in enumerate(qualities):
            assert q["quality"] == i + 1
            assert q["weight"] == 1


def test_evaluate__different_weights(assignment_quality):
    answer = mock.Mock()

    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion_ = mock.Mock()
        criterion_.objects.count.return_value = 1
        get_criterion.return_value = {
            "criterion": criterion_,
            "rules": mock.Mock(),
        }
        criterion = mock.Mock()
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda answer, rules: next(evaluations)
        criterion_.objects.get.return_value = criterion
        for i in range(3):
            UsesCriterion.objects.create(
                quality=assignment_quality,
                name="fake_{}".format(i + 1),
                version=0,
                rules=0,
                weight=i + 1,
            )

        quality_, qualities = assignment_quality.evaluate(answer)

        assert quality_ == ((1.0 * 1 + 2 * 2 + 3 * 3) / (1 + 2 + 3))
        for i, q in enumerate(qualities):
            assert q["quality"] == i + 1
            assert q["weight"] == i + 1


def test_add_criterion(assignment_quality):

    with mock.patch(
        "quality.models.quality.get_criterion"
    ) as get_criterion, mock.patch(
        "quality.models.quality.UsesCriterion.save"
    ) as uses_criterion_save, mock.patch(
        "quality.models.quality.criterions"
    ) as criterions:

        criterion_class = mock.Mock()
        criterion_class.objects.filter.exists.return_value = True
        criterion_class.info.return_value = {"name": "test"}
        criterions_ = [{"criterion": criterion_class, "rules": mock.Mock()}]
        criterions.values.return_value = criterions_

        criterion = mock.Mock()
        criterion.pk = 0
        criterion_ = mock.Mock()
        criterion_.objects.get.return_value = criterion
        rules = mock.Mock()
        rules.pk = 0

        get_criterion.return_value = {"criterion": criterion, "rules": rules}

        assignment_quality.add_criterion("test")

        assert uses_criterion_save.called


def test_add_criterion__invalid_name(assignment_quality):
    with mock.patch("quality.models.quality.criterions") as criterions:

        criterions.values.return_value = []

        with pytest.raises(ValueError):
            assignment_quality.add_criterion("test")


def test_available(assignment_quality):

    with mock.patch("quality.models.quality.criterions") as criterions:
        criterions_ = [
            {"criterion": mock.Mock(), "rules": mock.Mock()} for _ in range(3)
        ]
        for criterion in criterions_:
            criterion["criterion"].objects.filter.exists.return_value = True
            criterion["criterion"].info.return_value = {"name": "a"}
        criterions.values.return_value = criterions_
        available_info = assignment_quality.available
        assert len(available_info) == 3
        for criterion_ in available_info:
            assert isinstance(criterion_, dict)
