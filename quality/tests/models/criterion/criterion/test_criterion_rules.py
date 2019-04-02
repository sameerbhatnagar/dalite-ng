import pytest
from mixer.backend.django import mixer

from quality.models import CriterionRules


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_str():
    class FakeCriterionRules(CriterionRules):
        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion_rules = mixer.blend(FakeCriterionRules, threshold=0.5)

        with pytest.raises(NotImplementedError):
            str(fake_criterion_rules)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_get_or_create():
    class FakeCriterionRules(CriterionRules):
        class Meta:
            app_label = "quality"

    with mixer.ctx(commit=False):
        fake_criterion_rules = mixer.blend(FakeCriterionRules, threshold=0.5)

        with pytest.raises(NotImplementedError):
            fake_criterion_rules.get_or_create()
