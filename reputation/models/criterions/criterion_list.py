# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from reputation.logger import logger

from .errors import CriterionDoesNotExistError

criterions = {}


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
