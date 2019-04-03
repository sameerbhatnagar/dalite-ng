import logging

from .criterions import (
    MinCharsCriterion,
    MinCharsCriterionRules,
    MinWordsCriterion,
    MinWordsCriterionRules,
    NegWordsCriterion,
    NegWordsCriterionRules,
    RightAnswerCriterion,
    RightAnswerCriterionRules,
)
from .errors import CriterionDoesNotExistError

logger = logging.getLogger("quality")

criterions = {
    "min_words": {
        "criterion": MinWordsCriterion,
        "rules": MinWordsCriterionRules,
    },
    "min_chars": {
        "criterion": MinCharsCriterion,
        "rules": MinCharsCriterionRules,
    },
    "neg_words": {
        "criterion": NegWordsCriterion,
        "rules": NegWordsCriterionRules,
    },
    "right_answer": {
        "criterion": RightAnswerCriterion,
        "rules": RightAnswerCriterionRules,
    },
}


def get_criterion(criterion):
    """
    Returns the criterion class corresponding to the given `criterion` name.

    Parameters
    ----------
    criterion : str
        Name of the criterion

    Returns
    -------
    Criterion class
        Corresponding criterion class

    Raises
    ------
    CriterionDoesNotExistError
        If there is not criterion corresponding to the name `criterion`
    """
    try:
        return criterions[criterion]
    except KeyError:
        msg = "There is not criterion with the name {}.".format(criterion)
        logger.error(msg)
        raise CriterionDoesNotExistError(msg)
