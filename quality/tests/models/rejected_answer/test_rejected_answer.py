# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from quality.models import RejectedAnswer
from quality.tests.fixtures import global_quality  # noqa


def test_add_and_dict(global_quality):
    rationale = "random string"
    reasons = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]

    bad_answer = RejectedAnswer.add(global_quality, rationale, reasons)

    data = dict(bad_answer)
    assert data["rationale"] == rationale
    assert data["reasons"] == reasons
