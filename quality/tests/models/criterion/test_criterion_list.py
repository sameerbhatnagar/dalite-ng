import pytest

from quality.models import Criterion, CriterionRules
from quality.models.criterion import get_criterion
from quality.models.criterion.criterion_list import criterions
from quality.models.criterion.errors import CriterionDoesNotExistError


def test_get_criterion():
    for criterion in criterions:
        criterion_ = get_criterion(criterion)
        assert issubclass(criterion_["criterion"], Criterion)
        assert hasattr(criterion_["criterion"], "name")
        assert hasattr(criterion_["criterion"], "evaluate")
        assert issubclass(criterion_["rules"], CriterionRules)


def test_get_criterion__wrong():
    with pytest.raises(CriterionDoesNotExistError):
        criterion = get_criterion("fake_critertion")
