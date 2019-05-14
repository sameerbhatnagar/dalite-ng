# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from reputation.models import Criterion
from reputation.models.criterion_list import criterions, get_criterion
from reputation.models.criterions.errors import CriterionDoesNotExistError


def test_get_criterion():
    for criterion in criterions:
        criterion_ = get_criterion(criterion)
        assert issubclass(criterion_, Criterion)
        assert hasattr(criterion_, "name")
        assert hasattr(criterion_, "evaluate")


def test_get_criterion__wrong():
    with pytest.raises(CriterionDoesNotExistError):
        criterion = get_criterion("fake_critertion")
