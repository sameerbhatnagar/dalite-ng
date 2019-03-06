import logging

from .criterion import CriterionDoesNotExistError
from .min_chars import MinCharsCriterion
from .min_words import MinWordsCriterion

logger = logging.getLogger("quality")

criterions = {"min_words": MinWordsCriterion, "min_chars": MinCharsCriterion}


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
