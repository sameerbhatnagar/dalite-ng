# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest
from django.db import models
from mixer.backend.django import mixer

from quality.models import Criterion, CriterionRules
from quality.models.criterion.criterion import CriterionDoesNotExistError


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_evaluate_method():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.evaluate(None, None)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_info_method():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.info()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_serialize_method():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.serialize(None)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_name():
    class FakeCriterion(Criterion):
        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.save()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_rules():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False), mock.patch(
        "quality.models.criterion.criterion.models.Model.save"
    ):
        fake_criterion = mixer.blend(FakeCriterion)

        fake_criterion.uses_rules = "a,b,c,d"
        fake_criterion.save()
        assert fake_criterion.rules == ["a", "b", "c", "d"]

        fake_criterion.uses_rules = "e, f, g, h"
        fake_criterion.save()
        assert fake_criterion.rules == ["e", "f", "g", "h"]

        fake_criterion.uses_rules = "i , j , k , l"
        fake_criterion.save()
        assert fake_criterion.rules == ["i", "j", "k", "l"]


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_rules_needs_get_or_create_method():
    class FakeCriterionRules(CriterionRules):
        name = models.CharField(max_length=32, default="fake", editable=False)

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion_rules = mixer.blend(FakeCriterionRules)

        with pytest.raises(NotImplementedError):
            fake_criterion_rules.get_or_create()


def test_criterion_does_not_exists__no_msg():
    with pytest.raises(CriterionDoesNotExistError) as e:
        raise CriterionDoesNotExistError()
    assert (
        "There is no criterion corresponding to that name or version."
        in str(e.value)
    )


def test_criterion_does_not_exists__msg():
    msg = "error msg"
    with pytest.raises(CriterionDoesNotExistError) as e:
        raise CriterionDoesNotExistError(msg)
    assert msg in str(e.value)
