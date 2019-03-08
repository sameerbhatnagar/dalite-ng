import mock
import pytest
from django.db import models
from mixer.backend.django import mixer

from quality.models import CriterionRules


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_get_or_create():
    class FakeCriterionRules(CriterionRules):
        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion_rules = mixer.blend(FakeCriterionRules)

        with pytest.raises(NotImplementedError):
            fake_criterion_rules.get_or_create()


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_dict():
    class FakeCriterionRules(CriterionRules):
        a = models.PositiveIntegerField()
        b = models.PositiveIntegerField()
        c = models.PositiveIntegerField()

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False), mock.patch(
        "quality.models.criterion.criterion.models.Model.save"
    ):
        fake_rules = mixer.blend(FakeCriterionRules, a=1, b=2, c=3)

        data = dict(fake_rules)
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 3
        assert len(data) == 3
