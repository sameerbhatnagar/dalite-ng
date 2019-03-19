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
        a = models.PositiveIntegerField(verbose_name="A", help_text="aa")
        b = models.PositiveIntegerField(verbose_name="B", help_text="bb")
        c = models.PositiveIntegerField(verbose_name="C", help_text="cc")

        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False), mock.patch(
        "quality.models.criterion.criterion.models.Model.save"
    ):
        fake_rules = mixer.blend(
            FakeCriterionRules, threshold=1, a=1, b=2, c=3
        )

        data = dict(fake_rules)
        assert len(data) == 4
        assert data["threshold"]["name"] == "threshold"
        assert data["threshold"]["full_name"] == "Threshold"
        assert (
            data["threshold"]["description"]
            == "Minimum value for the answer to be accepted"
        )
        assert data["threshold"]["value"] == 1
        assert data["threshold"]["type"] == "FloatField"
        assert len(data["threshold"]) == 5
        assert data["a"]["name"] == "a"
        assert data["a"]["full_name"] == "A"
        assert data["a"]["description"] == "aa"
        assert data["a"]["value"] == 1
        assert data["a"]["type"] == "PositiveIntegerField"
        assert len(data["a"]) == 5
        assert data["b"]["name"] == "b"
        assert data["b"]["full_name"] == "B"
        assert data["b"]["description"] == "bb"
        assert data["b"]["value"] == 2
        assert data["b"]["type"] == "PositiveIntegerField"
        assert len(data["b"]) == 5
        assert data["c"]["name"] == "c"
        assert data["c"]["full_name"] == "C"
        assert data["c"]["description"] == "cc"
        assert data["c"]["value"] == 3
        assert data["c"]["type"] == "PositiveIntegerField"
        assert len(data["c"]) == 5
