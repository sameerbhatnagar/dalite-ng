# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock

from quality.models import Quality, UsesCriterion


def test_evaluate__no_criterions():
    quality = Quality.objects.create()
    answer = mock.Mock()

    quality_, qualities = quality.evaluate(answer)

    assert quality_ is None
    assert qualities == []


def test_evaluate__all_equal():
    quality = Quality.objects.create()
    answer = mock.Mock()

    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion_ = mock.Mock()
        criterion_.objects.count.return_value = 1
        get_criterion.return_value = criterion_
        criterion = mock.Mock()
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda answer, rules: next(evaluations)
        criterion_.objects.get.return_value = criterion
        for i in range(3):
            UsesCriterion.objects.create(
                quality=quality,
                name="fake_{}".format(i + 1),
                version=0,
                rules=0,
                weight=1,
            )

        quality_, qualities = quality.evaluate(answer)

        assert quality_ == (1.0 + 2 + 3) / 3
        for i, q in enumerate(qualities):
            assert q["quality"] == i + 1
            assert q["weight"] == 1


def test_evaluate__different_weights():
    quality = Quality.objects.create()
    answer = mock.Mock()

    with mock.patch("quality.models.quality.get_criterion") as get_criterion:
        criterion_ = mock.Mock()
        criterion_.objects.count.return_value = 1
        get_criterion.return_value = criterion_
        criterion = mock.Mock()
        evaluations = (i + 1 for i in range(3))
        criterion.evaluate = lambda answer, rules: next(evaluations)
        criterion_.objects.get.return_value = criterion
        for i in range(3):
            UsesCriterion.objects.create(
                quality=quality,
                name="fake_{}".format(i + 1),
                version=0,
                rules=0,
                weight=i + 1,
            )

        quality_, qualities = quality.evaluate(answer)

        assert quality_ == ((1.0 * 1 + 2 * 2 + 3 * 3) / (1 + 2 + 3))
        for i, q in enumerate(qualities):
            assert q["quality"] == i + 1
            assert q["weight"] == i + 1
