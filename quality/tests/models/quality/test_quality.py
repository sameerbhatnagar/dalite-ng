# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest
from django.db import models
from mixer.backend.django import mixer

from quality.models import Criterion, Quality, UsesCriterion
from quality.models.criterion.criterion import (
    CriterionDoesNotExistError,
    CriterionExistsError,
)


def test_evaluate_all_equal():
    quality = Quality.objects.create()
    answer = mock.Mock()

    with mock.patch(
        "quality.models.quality.get_criterion", return_value=mock.Mock()
    ) as criterion_:
        criterion_.objects.count.return_value = 1
        criterions = [mock.Mock() for _ in range(3)]
        for i, criterion in enumerate(criterions):
            criterion.evaluate.return_value = i + 1
        criterion_.objects.get = mock.Mock(return_value=criterions)
        for i in range(3):
            UsesCriterion.objects.create(
                quality=quality,
                name="fake_{}".format(i + 1),
                version=0,
                use_latest=True,
                weight=1,
            )

        quality_, qualities = quality.evaluate(answer)
