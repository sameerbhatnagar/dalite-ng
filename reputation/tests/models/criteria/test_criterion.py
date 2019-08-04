# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest
from django.core.exceptions import ValidationError
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

        assert len(data) == 6
        assert "version" in data
        assert "points_per_threshold" in data
        assert "thresholds" in data
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
def test_save__points_len_equal_thresholds_length():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False), mock.patch(
        "reputation.models.criteria.criterion.Criterion.save"
    ):
        fake_criterion = mixer.blend(
            FakeCriterion, points_per_threshold="1,2,3", thresholds="1,2,3"
        )

        fake_criterion.save()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_save__points_len_one_more_than_thresholds_length():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False), mock.patch(
        "reputation.models.criteria.criterion.Criterion.save"
    ):
        fake_criterion = mixer.blend(
            FakeCriterion, points_per_threshold="1,2,3", thresholds="1,2"
        )

        fake_criterion.save()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_save__points_len_more_than_one_than_thresholds_length():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(
            FakeCriterion, points_per_threshold="1,2,3", thresholds="1"
        )

        with pytest.raises(ValidationError):
            fake_criterion.save()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_save__points_len_less_than_thresholds_length():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "reputation"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(
            FakeCriterion, points_per_threshold="1,2", thresholds="1,2,3"
        )

        with pytest.raises(ValidationError):
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
