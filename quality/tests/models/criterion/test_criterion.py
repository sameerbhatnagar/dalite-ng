# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.db import models
from mixer.backend.django import mixer

from quality.models import Criterion
from quality.models.criterion.criterion import (
    CriterionDoesNotExistError,
    CriterionExistsError,
)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_evaluate_method():
    class FakeCriterion(Criterion):
        name = models.CharField(max_length=32)

        class Meta:
            app_label = "quality"

        def save(self, *args, **kwargs):
            self.name = "fake"
            super(FakeCriterion, self).save(self, *args, **kwargs)

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.evaluate(None)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_criterion_needs_name():
    class FakeCriterion(Criterion):
        class Meta:
            app_label = "quality"

        pass

    with mixer.ctx(commit=False):
        fake_criterion = mixer.blend(FakeCriterion)

        with pytest.raises(NotImplementedError):
            fake_criterion.save()


def test_criterion_exists__no_msg():
    with pytest.raises(CriterionExistsError) as e:
        raise CriterionExistsError()
    assert "A criterion with the same options already exists." in str(e.value)


def test_criterion_exists__msg():
    msg = "error msg"
    with pytest.raises(CriterionExistsError) as e:
        raise CriterionExistsError(msg)
    assert msg in str(e.value)


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
