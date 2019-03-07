__all__ = [
    "Criterion",
    "CriterionRules",
    "MinCharsCriterion",
    "MinCharsCriterionRules",
    "MinWordsCriterion",
    "MinWordsCriterionRules",
    "get_criterion",
]


from .criterion import Criterion, CriterionRules
from .criterion_list import get_criterion
from .criterions import (
    MinCharsCriterion,
    MinCharsCriterionRules,
    MinWordsCriterion,
    MinWordsCriterionRules,
)
