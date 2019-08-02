# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from reputation.models import NQuestionsCriterion, ReputationType


@pytest.fixture
def n_questions_criterion():
    criterion = NQuestionsCriterion.objects.create()
    criterion.for_reputation_types.add(
        ReputationType.objects.get(type="teacher")
    )
    return criterion
