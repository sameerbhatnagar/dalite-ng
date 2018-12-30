# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from peerinst.models import (
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupAssignment,
    Teacher,
)

from .decorators import group_access_required

logger = logging.getLogger("peerinst-views")


def validate_update_data(req):
    try:
        data = json.loads(req.body)
    except ValueError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    try:
        name = data["name"]
        value = data["value"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    return name, value


@login_required
@require_http_methods(["GET"])
@group_access_required
def group_details_page(req, group_hash, teacher, group):

    assignments = StudentGroupAssignment.objects.filter(group=group)

    context = {"group": group, "assignments": assignments, "teacher": teacher}
    print(group.student_id_needed)

    return render(req, "peerinst/group/details.html", context)


@login_required
@require_http_methods(["POST"])
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
            resp = TemplateResponse(
                req,
                "400.html",
                context={"message": _("That name already exists.")},
            )
            return HttpResponseBadRequest(resp.render())
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
            resp = TemplateResponse(
                req,
                "400.html",
                context={
                    "message": _(
                        "There is no teacher with username {}.".format(teacher)
                    )
                },
            )
            return HttpResponseBadRequest(resp.render())
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
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render())

    return HttpResponse(content_type="text/plain")


@login_required
@require_http_methods(["GET"])
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
    }

    return render(req, "peerinst/group/assignment.html", context)


@login_required
@require_http_methods(["POST"])
@group_access_required
def group_assignment_remove(req, assignment_hash, teacher, group, assignment):
    assignment.delete()
    return HttpResponse()


@login_required
@require_http_methods(["POST"])
@group_access_required
def group_assignment_update(req, assignment_hash, teacher, group, assignment):

    name, value = validate_update_data(req)
    if isinstance(name, HttpResponse):
        return name

    err = assignment.update(name, value)

    if err is not None:
        resp = TemplateResponse(req, "400.html", context={"message": err})
        return HttpResponseBadRequest(resp.render())

    return HttpResponse(content_type="text/plain")


@login_required
@require_http_methods(["POST"])
@group_access_required
def send_student_assignment(req, assignment_hash, teacher, group, assignment):

    try:
        data = json.loads(req.body)
    except ValueError:
        print(1)
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    try:
        email = data["email"]
    except KeyError:
        print(2)
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    try:
        student = Student.objects.get(student__email=email)
    except Student.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'There is no student with email "{}".'.format(email)
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    student_assignment, __ = StudentAssignment.objects.get_or_create(
        group_assignment=assignment, student=student
    )

    err = student_assignment.send_email("new_assignment")

    if err is not None:
        resp = TemplateResponse(req, "500.html", context={"message": _(err)})
        return HttpResponseServerError(resp.render())

    return HttpResponse()


@login_required
@require_http_methods(["GET"])
@group_access_required
def get_assignment_student_progress(
    req, assignment_hash, teacher, group, assignment
):
    data = assignment.get_student_progress()
    return JsonResponse(data, safe=False)
