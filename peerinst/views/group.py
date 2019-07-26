# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_safe

from dalite.views.errors import response_400, response_500
from peerinst.models import (
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupAssignment,
    Teacher,
)

from ..gradebooks import group_gradebook, groupassignment_gradebook
from .decorators import group_access_required

logger = logging.getLogger("peerinst-views")


def validate_update_data(req):
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(req, msg=_("Wrong data type was sent."))

    try:
        name = data["name"]
        value = data["value"]
    except KeyError:
        return response_400(req, msg=_("There are missing parameters."))

    return name, value


@login_required
@require_safe
@group_access_required
def group_details_page(req, group_hash, teacher, group):

    assignments = StudentGroupAssignment.objects.filter(group=group)

    context = {"group": group, "assignments": assignments, "teacher": teacher}

    return render(req, "peerinst/group/details.html", context)


@login_required
@require_POST
@group_access_required
def group_details_update(req, group_hash, teacher, group):
    """
    Updates the field of the group using the `name` and `value` given by the
    post request data.

    Parameters
    ----------
    group_hash : str
        Hash of the group
    teacher : Teacher
    group : StudentGroup
        Group corresponding to the hash (returned by `group_access_required`)

    Returns
    -------
    HttpResponse
        Either an empty 200 response if everything worked or an error response
    """

    name, value = validate_update_data(req)
    if isinstance(name, HttpResponse):
        return name

    if name == "name":
        if (
            name != group.name
            and StudentGroup.objects.filter(name=name).exists()
        ):
            return response_400(req, msg=_("That name already exists."))
        group.name = value
        group.save()
        logger.info("Group %d's name was changed to %s.", group.pk, value)

    elif name == "title":
        group.title = value
        group.save()
        logger.info("Group %d's title was changed to %s.", group.pk, value)

    elif name == "teacher":
        try:
            teacher = Teacher.objects.get(user__username=value)
        except Teacher.DoesNotExist:
            return response_400(
                req,
                msg=_("There is no teacher with username {}.".format(teacher)),
            )
        group.teacher.add(teacher)
        group.save()
        logger.info("Teacher %d was added to group %d.", value, group.pk)

    elif name == "student_id_needed":
        group.student_id_needed = value
        group.save()
        logger.info(
            "Student id needed was set to %s for group %d.", value, group.pk
        )

    else:
        return response_400(req, msg=_("Wrong data type was sent."))

    return HttpResponse(content_type="text/plain")


@login_required
@require_safe
@group_access_required
def group_assignment_page(req, assignment_hash, teacher, group, assignment):

    context = {
        "teacher_id": teacher.id,
        "group": group,
        "assignment": assignment,
        "questions": assignment.questions,
        "students_with_answers": assignment.assignment.answer_set.values_list(
            "user_token", flat=True
        ),
        "data": json.dumps(
            {
                "assignment": {
                    "hash": assignment.hash,
                    "distribution_date": assignment.distribution_date.isoformat()  # noqa
                    if assignment.distribution_date
                    else None,
                },
                "urls": {
                    "get_assignment_student_progress": reverse(
                        "get-assignment-student-progress",
                        kwargs={"assignment_hash": assignment.hash},
                    ),
                    "send_student_assignment": reverse(
                        "send-student-assignment",
                        kwargs={"assignment_hash": assignment.hash},
                    ),
                    "group_assignment_update": reverse(
                        "group-assignment-update",
                        kwargs={"assignment_hash": assignment.hash},
                    ),
                    "distribute_assignment": reverse(
                        "distribute-assignment",
                        kwargs={"assignment_hash": assignment.hash},
                    ),
                },
                "translations": {
                    "distribute": ugettext("Distribute"),
                    "distributed": ugettext("Distributed"),
                },
            }
        ),
    }

    return render(req, "peerinst/group/assignment.html", context)


@login_required
@require_POST
@group_access_required
def group_assignment_remove(req, assignment_hash, teacher, group, assignment):
    assignment.delete()
    return HttpResponse()


@login_required
@require_POST
@group_access_required
def group_assignment_update(req, assignment_hash, teacher, group, assignment):

    name, value = validate_update_data(req)
    if isinstance(name, HttpResponse):
        return name

    err = assignment.update(name, value)

    if err is not None:
        return response_400(req, msg=_(err))

    return HttpResponse(content_type="text/plain")


@login_required
@require_POST
@group_access_required
def send_student_assignment(req, assignment_hash, teacher, group, assignment):

    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(req, msg=_("Wrong data type was sent."))

    try:
        email = data["email"]
    except KeyError:
        return response_400(req, msg=_("There are missing parameters."))

    try:
        student = Student.objects.get(student__email=email)
    except Student.DoesNotExist:
        return response_400(
            req, msg=_('There is no student with email "{}".'.format(email))
        )

    student_assignment, __ = StudentAssignment.objects.get_or_create(
        group_assignment=assignment, student=student
    )

    err = student_assignment.send_email("new_assignment")

    if err is not None:
        return response_500(req, msg=_(err))

    return HttpResponse()


@login_required
@require_safe
@group_access_required
def get_assignment_student_progress(
    req, assignment_hash, teacher, group, assignment
):
    data = {"progress": assignment.student_progress}

    return JsonResponse(data)


@login_required
@require_POST
@group_access_required
def distribute_assignment(req, assignment_hash, teacher, group, assignment):
    """
    Distributes the assignment to students.
    """
    assignment.distribute()
    data = {
        "hash": assignment.hash,
        "distribution_date": assignment.distribution_date.isoformat()  # noqa
        if assignment.distribution_date
        else None,
    }
    return JsonResponse(data)


@login_required
@require_safe
@group_access_required
def csv_gradebook(req, group_hash, teacher, group):
    """
    Returns the csv gradebook for the given `group` in a stream.

    Parameters
    ----------
    group_hash : str
        Hash of the group
    teacher : Teacher
        Teacher corresponding to the requested (returned by
        `group_access_required`) (not used)
    group : StudentGroup
        Group corresponding to the hash (returned by `group_access_required`)

    Returns
    -------
    HttpResponse
        Either a streaming 200 response with the csv data if everything worked
        or an error response
    """
    filename = "myDALITE_gradebook_{}.csv".format(group)
    gradebook_gen = group_gradebook(group)
    resp = StreamingHttpResponse(gradebook_gen, content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    return resp


@login_required
@require_safe
@group_access_required
def csv_assignment_gradebook(
    req, group_hash, assignment_hash, teacher, group, assignment
):
    """
    Returns the csv gradebook for the given `group_assignment` in a stream.

    Parameters
    ----------
    group_hash : str
        Hash of the group
    assignment_hash : str
        Hash of the group_assignment
    teacher : Teacher
        Teacher corresponding to the requested (returned by
        `group_access_required`) (not used)
    group : StudentGroup
        Group corresponding to the hash (returned by `group_access_required`)
    assignment : StudentGroupAssignment
        group_assignment corresponding to the hash
        (`returned by group_access_required`)

    Returns
    -------
    HttpResponse
        Either a streaming 200 response with the csv data if everything worked
        or an error response
    """
    filename = "myDALITE_gradebook_{}_{}.csv".format(group, assignment)
    gradebook_gen = groupassignment_gradebook(group, assignment)
    resp = StreamingHttpResponse(gradebook_gen, content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    return resp
