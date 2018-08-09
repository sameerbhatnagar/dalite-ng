# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

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
import pytz

from peerinst.models import StudentGroup, StudentGroupAssignment, Teacher


def group_access_required(fct):
    def wrapper(req, *args, **kwargs):
        group_hash = kwargs.get("group_hash", None)
        assignment_hash = kwargs.get("assignment_hash", None)
        return_assignment = assignment_hash is not None

        if group_hash is not None or assignment_hash is not None:

            user = req.user
            try:
                teacher = Teacher.objects.get(user=user)
            except Teacher.DoesNotExist:
                resp = TemplateResponse(
                    req,
                    "403.html",
                    context={
                        "message": _("You don't have access to this resource.")
                    },
                )
                return HttpResponseForbidden(resp.render())

            if group_hash is not None:
                group = StudentGroup.get(group_hash)
                if group is None:
                    resp = TemplateResponse(
                        req,
                        "400.html",
                        context={
                            "message": _(
                                'There is no group with hash "{}".'.format(
                                    group_hash
                                )
                            )
                        },
                    )
                    return HttpResponseBadRequest(resp.render())

            else:
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
                group = assignment.group

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

            if return_assignment:
                return fct(
                    req,
                    *args,
                    teacher=teacher,
                    group=group,
                    assignment=assignment,
                    **kwargs
                )
            else:
                return fct(req, *args, teacher=teacher, group=group, **kwargs)

        else:
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _("You don't have access to this resource.")
                },
            )
            return HttpResponseForbidden(resp.render())

    return wrapper


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

    return render(req, "peerinst/group/details.html", context)


@login_required
@require_http_methods(["POST"])
@group_access_required
def group_details_update(req, group_hash, teacher, group):

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
@group_access_required
def group_assignment_page(req, assignment_hash, teacher, group, assignment):

    context = {
        "teacher_id": teacher.id,
        "group_hash": group.hash,
        "assignment": assignment,
        "questions": assignment.assignment.questions.all(),
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

    print(name)

    if name == "due_date":
        assignment.due_date = datetime.strptime(
            value[:-5], "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=pytz.utc)
        assignment.save()

    else:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render())

    return HttpResponse(content_type="text/plain")
