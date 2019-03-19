# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from dalite.views.errors import response_400, response_403
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_safe
from peerinst.models import StudentGroupAssignment, Teacher

from ..models import Quality, QualityType, UsesCriterion
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

    if not assignment.group.teacher.filter(pk=teacher.pk).exists():
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
        assignment.quality = Quality.objects.create(
            quality_type=quality_type, threshold=1
        )
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
        "quality": dict(assignment.quality),
        "next": next_,
        "available": assignment.quality.available,
        "criterions": [
            dict(criterion)
            for criterion in assignment.quality.criterions.all()
        ],
        "urls": {
            "add_criterion": reverse("quality:add-criterion"),
            "update_criterion": reverse("quality:update-criterion"),
            "remove_criterion": reverse("quality:remove-criterion"),
        },
    }

    return render(req, "quality/edit/index.html", {"data": json.dumps(data)})


@login_required
@require_POST
def add_criterion(req):
    """
    Adds the given criterion to the quality with the given parameters. The
    request must have parameters:
        quality : int
            Primary key of the quality
        criterion : str
            Name of the criterion

    Returns
    -------
    HttpResponse
        Either a JsonResponse with the criterion data or an error response
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning,
        )
    try:
        quality_pk = data["quality"]
        criterion_name = data["criterion"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning,
        )

    try:
        quality = Quality.objects.get(pk=quality_pk)
    except Quality.DoesNotExist:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong."),
            logger_msg=(
                "There isn't any quality with key {}.".format(quality_pk)
            ),
            log=logger.warning,
        )

    try:
        criterion = quality.add_criterion(criterion_name)
    except ValueError:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong."),
            logger_msg=(
                "There isn't any quality with key {}.".format(quality_pk)
            ),
            log=logger.warning,
        )

    logger.info(
        "Criterion %s was added to quality %d.", criterion_name, quality_pk
    )

    return JsonResponse(dict(criterion))


@login_required
@require_POST
def update_criterion(req):
    """
    Mofieds the criterion for the quality. The request must have parameters:
        quality : int
            Primary key of the quality
        criterion : str
            Name of the criterion
        field : str
            Name of the field to update
        value : Any
            New value for the field

    Returns
    -------
    HttpResponse
        Either a JsonResponse with the criterion data or an error response
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning,
        )
    try:
        quality_pk = data["quality"]
        criterion_name = data["criterion"]
        field = data["field"]
        value = data["value"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning,
        )

    try:
        quality = Quality.objects.get(pk=quality_pk)
    except Quality.DoesNotExist:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong."),
            logger_msg=(
                "There isn't any quality with key {}.".format(quality_pk)
            ),
            log=logger.warning,
        )

    try:
        criterion, old_value = quality.update_criterion(
            criterion_name, field, value
        )
    except (AttributeError, UsesCriterion.DoesNotExist) as e:
        return response_400(
            req,
            msg=_("There was an error updating the criterion."),
            logger_msg=str(e),
            log=logger.warning,
        )

    logger.info(
        "Field %s for criterion %s in quality %d updated from %s to %s.",
        field,
        criterion_name,
        quality_pk,
        old_value,
        value,
    )

    return JsonResponse(dict(criterion))


@login_required
@require_POST
def remove_criterion(req):
    """
    REmoves the given criterion to the quality with the given parameters. The
    request must have parameters:
        quality : int
            Primary key of the quality
        criterion : str
            Name of the criterion

    Returns
    -------
    HttpResponse
        Either an empty HttpResponse or an error response
    """
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning,
        )
    try:
        quality_pk = data["quality"]
        criterion_name = data["criterion"]
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning,
        )

    try:
        quality = Quality.objects.get(pk=quality_pk)
    except Quality.DoesNotExist:
        return response_400(
            req,
            msg=_("Some of the parameters were wrong."),
            logger_msg=(
                "There isn't any quality with key {}.".format(quality_pk)
            ),
            log=logger.warning,
        )

    quality.remove_criterion(criterion_name)

    logger.info(
        "Criterion %s was removed from quality %d.", criterion_name, quality_pk
    )

    return HttpResponse()
