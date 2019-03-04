# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.db import models
from mixer.backend.django import mixer

from quality.models import Criterion


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
