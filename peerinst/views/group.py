# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
import json

from peerinst.models import StudentGroup, StudentGroupAssignment, Teacher


@login_required
@require_http_methods(["GET"])
def group_details_page(req, group_hash):
    teacher = _get_teacher(req)
    if isinstance(teacher, HttpResponse):
        return teacher

    group = _get_group(group_hash)
    if isinstance(group, HttpResponse):
        return group

    resp = _verify_group_access(teacher, group)
    if isinstance(resp, HttpResponse):
        return resp

    assignments = StudentGroupAssignment.objects.filter(group=group)

    context = {"group": group, "assignments": assignments, "teacher": teacher}

    return render(req, "peerinst/group/details.html", context)


@login_required
@require_http_methods(["POST"])
def group_details_update(req, group_hash):
    teacher = _get_teacher(req)
    if isinstance(teacher, HttpResponse):
        return teacher

    group = _get_group(group_hash)
    if isinstance(group, HttpResponse):
        return group

    resp = _verify_group_access(teacher, group)
    if isinstance(resp, HttpResponse):
        return resp

    if req.META["CONTENT_TYPE"] != "application/json":
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        data = json.loads(req.body)
    except ValueError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        name = data["name"]
        value = data["value"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

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

    elif name == "title":
        group.title = value
        group.save()

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
def group_assignment_page(req, assignment_hash):
    teacher = _get_teacher(req)
    if isinstance(teacher, HttpResponse):
        return teacher

    assignment = _get_assignment(assignment_hash)
    if isinstance(assignment, HttpResponse):
        return assignment

    resp = _verify_group_access(teacher, assignment.group)
    if isinstance(resp, HttpResponse):
        return resp

    context = {
        "teacher_id": teacher.id,
        "group_hash": assignment.group.hash,
        "assignment": assignment,
    }

    return render(req, "peerinst/group/assignment.html", context)


def _get_teacher(req):
    user = req.user
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        resp = TemplateResponse(
            req,
            "403.html",
            context={"message": _("You don't have access to this resource.")},
        )
        return HttpResponseForbidden(resp.render())
    return teacher


def _get_group(group_hash):
    group = StudentGroup.get(group_hash)
    if group is None:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'There is no group with hash "{}".'.format(group_hash)
                )
            },
        )
        return HttpResponseBadRequest(resp.render())
    return group


def _get_assignment(assignment_hash):
    assignment = StudentGroupAssignment.get(assignment_hash)
    if assignment is None:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'There is no assignment with hash "{}".'.format(
                        assignment_hash
                    )
                )
            },
        )
        return HttpResponseBadRequest(resp.render())
    return assignment


def _verify_group_access(teacher, group):
    if teacher not in group.teacher.all():
        resp = TemplateResponse(
            req,
            "403.html",
            context={
                "message": _(
                    "You don't have access to this resource. You must be "
                    "registered as a teacher for the group {}.".format(
                        group.name
                    )
                )
            },
        )
        return HttpResponseForbidden(resp.render())
    return None
