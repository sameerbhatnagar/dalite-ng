# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_safe

from dalite.views.errors import response_400, response_403
from peerinst.models import StudentGroupAssignment, Teacher

from ..models import Quality, QualityType
from .decorators import logged_in_non_student_required

logger = logging.getLogger("quality")


def verify_assignment(req, assignment_pk):
    """
    Verifies if the assignment exists and the user is allowed to change the
    assignment, returning it if that's the case and an error response if not.

    Parameters
    ----------
    req : HttpRequest
        Request
    assignment_pk : int
        Primary key for the assignment

    Returns
    -------
    Either
        StudentGroupAssignment
            Assignment corresponding to the primary key
        HttpResponse
            400 or 403 error response
    """
    try:
        assignment = StudentGroupAssignment.objects.get(pk=assignment_pk)
    except StudentGroupAssignment.DoesNotExist:
        return response_400(
            req,
            msg=_("Some parameters are wrong"),
            logger_msg=(
                "An access to {} was tried with the wrong ".format(req.path)
                + "assignment primary key {}.".format(assignment_pk)
            ),
            log=logger.warning,
        )

    try:
        teacher = Teacher.objects.get(user=req.user)
    except Teacher.DoesNotExist:
        return response_403(
            req,
            msg=_("You don't have access to this resource."),
            logger_msg=(
                "Access to {} from user {}.".format(req.path, req.user.pk)
            ),
            log=logger.warning,
        )

    quality_type = QualityType.objects.get(type="assignment")
    if assignment.quality is None:
        assignment.quality = Quality.objects.create(quality_type=quality_type)
        assignment.save()

    return assignment


@logged_in_non_student_required
@require_safe
def index(req):
    """
    Returns the main page where it's possible to edit the quality.
    Possible query arguments are:
        assignment : int
            Primary key for a StudentGroupAssignment. If no Quality is
            associated with it, will be created
        next : str
            Page to return to once the edition is done. If not given, will go
            to /welcome
    If no query string is given, an error will be returned

    Returns
    -------
    HttpResponse
        Either a TemplateResponse for edition or an error response
    """
    assignment_pk = req.GET.get("assignment")
    next_ = req.GET.get("next")

    if assignment_pk is None:
        return response_400(
            req,
            msg=_("Some parameters are missing"),
            logger_msg=(
                "An access to {} was tried without a ".format(req.path)
                + "primary key in the query string indicating what the "
                "quality was for."
            ),
            log=logger.error,
        )

    if assignment_pk is not None:
        assignment = verify_assignment(req, assignment_pk)
        if isinstance(assignment, HttpResponse):
            return assignment

    data = {
        "quality_type": assignment.quality.quality_type.type,
        "next": next_,
        "available": assignment.quality.available,
        "criterions": [
            dict(criterion)
            for criterion in assignment.quality.criterions.all()
        ],
    }

    return render(req, "quality/edit/index.html", {"data": json.dumps(data)})


@login_required
@require_POST
def add_criterion(req):
    pass
