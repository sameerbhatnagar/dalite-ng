import pytest

from quality.models import Criterion
from quality.models.criterion import get_criterion
from quality.models.criterion.errors import CriterionDoesNotExistError


def test_get_criterion():
    criterions = ("min_words",)
    for criterion in criterions:
        criterion_ = get_criterion(criterion)
        assert issubclass(criterion_, Criterion)
        assert hasattr(criterion_, "name")
        assert hasattr(criterion_, "evaluate")


def test_get_criterion__wrong():
    with pytest.raises(CriterionDoesNotExistError):
        criterion = get_criterion("fake_critertion")
