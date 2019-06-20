# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.db import models
from mixer.backend.django import mixer

from reputation.models import Criterion


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_dict():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

        @staticmethod
        def info():
            return {"name": "fake", "full_name": "fake", "description": "fake"}

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        data = dict(fake_criterion)

        assert "version" in data
        assert "badge_threshold" in data
        assert "name" in data
        assert "full_name" in data
        assert "description" in data


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_save__missing_name():
    class FakeCriterion(Criterion):
        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.save()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_info__not_implemented():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.info()
