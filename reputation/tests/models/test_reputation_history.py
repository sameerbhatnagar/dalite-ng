# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import mock

from peerinst.tests.fixtures import *  # noqa
from reputation.models import ReputationHistory
from reputation.tests.fixtures import *  # noqa


def test_create(teacher_reputation):
    reputation = (
        1,
        [
            {
                "name": "fake",
                "full_name": "fake",
                "description": "fake",
                "version": 1,
                "weight": 1,
                "reputation": 1,
            }
        ],
    )
    with mock.patch.object(
        teacher_reputation, "evaluate", return_value=reputation
    ):

        history_elem = ReputationHistory.create(teacher_reputation)

        assert history_elem.reputation.pk == teacher_reputation.pk
        assert history_elem.reputation_value == reputation[0]
        assert json.loads(history_elem.reputation_details) == reputation[1]
