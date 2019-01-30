# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.template.response import TemplateResponse

logger = logging.getLogger("dalite")


def response_400(req, msg="", logger_msg="", log=None):
    """
    Returns a 400 error with the passed in msg, logging at the same time.

    Parameters
    ----------
    req ; HttpRequest
        Request
    msg : str (default : "")
        Message to add to the template
    logger_msg : str (default : "")
        Message to log
    log : Optional[Callable[[], None]] (default : None)
        Function to use to log. If None, will log a warning with "dalite"
        logger
    """
    if not logger_msg:
        logger_msg = "400 error for user {} on path {}.".format(
            req.user, req.path
        )
    if log is None:
        log = logger.warning

    log(logger_msg)

    return TemplateResponse(
        req, "400.html", context={"message": msg}, status=400
    )


def response_403(req, msg="", logger_msg="", log=None):
    """
    Returns a 403 error with the passed in msg, logging at the same time.

    Parameters
    ----------
    req ; HttpRequest
        Request
    msg : str (default : "")
        Message to add to the template
    logger_msg : str (default : "")
        Message to log
    log : Optional[Callable[[], None]] (default : None)
        Function to use to log. If None, will log a warning with "dalite"
        logger
    """
    if not logger_msg:
        logger_msg = "403 error for user {} on path {}.".format(
            req.user, req.path
        )
    if log is None:
        log = logger.warning

    log(logger_msg)

    return TemplateResponse(
        req, "403.html", context={"message": msg}, status=403
    )


def response_404(req, msg="", logger_msg="", log=None):
    """
    Returns a 404 error with the passed in msg, logging at the same time.

    Parameters
    ----------
    req ; HttpRequest
        Request
    msg : str (default : "")
        Message to add to the template
    logger_msg : str (default : "")
        Message to log
    log : Optional[Callable[[], None]] (default : None)
        Function to use to log. If None, will log a warning with "dalite"
        logger
    """
    if not logger_msg:
        logger_msg = "404 error for user {} on path {}.".format(
            req.user, req.path
        )
    if log is None:
        log = logger.warning

    log(logger_msg)

    return TemplateResponse(
        req, "404.html", context={"message": msg}, status=404
    ).render()


def response_500(req, msg="", logger_msg="", log=None):
    """
    Returns a 500 error with the passed in msg, logging at the same time.

    Parameters
    ----------
    req ; HttpRequest
        Request
    msg : str (default : "")
        Message to add to the template
    logger_msg : str (default : "")
        Message to log
    log : Optional[Callable[[], None]] (default : None)
        Function to use to log. If None, will log a warning with "dalite"
        logger
    """
    if not logger_msg:
        logger_msg = "500 error for user {} on path {}.".format(
            req.user, req.path
        )
    if log is None:
        log = logger.warning

    log(logger_msg)

    return TemplateResponse(
        req, "500.html", context={"message": msg}, status=500
    )
