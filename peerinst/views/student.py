# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
import pytz
import json
import logging

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from ..models import Student, StudentAssignment, StudentGroup
from ..students import (
    authenticate_student,
    create_student_token,
    get_student_username_and_password,
)

logger = logging.getLogger("peerinst-views")


@require_http_methods(["GET"])
def index_page(req):
    """
    Main student page. Accessed through a link sent by email containing
    a token or without the token for a logged in student.
    """

    token = req.GET.get("token")

    # get student from token or from logged in user
    if token is None:
        if not isinstance(req.user, User):
            logger.warning(
                "Student index page accessed without a token or being logged "
                "in."
            )
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _(
                        "You must be a logged in student to access this "
                        "resource."
                    )
                },
            )
            return HttpResponseForbidden(resp.render())

        try:
            student = Student.objects.get(student=req.user)
        except Student.DoesNotExist:
            logger.warning(
                "There is no student corresponding to user %d.", req.user.pk
            )
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _(
                        "You must be a logged in student to access this "
                        "resource."
                    )
                },
            )
            return HttpResponseForbidden(resp.render())
        token = create_student_token(
            student.student.username, student.student.email
        )
    else:
        user = authenticate_student(req, token)
        if isinstance(user, HttpResponse):
            return user
        logout(req)
        login(req, user)
        try:
            student = Student.objects.get(student=user)
        except Student.DoesNotExist:
            logger.warning(
                "There is no student corresponding to user %d.", user.pk
            )
            resp = TemplateResponse(
                req,
                "403.html",
                context={
                    "message": _(
                        "You must be a logged in student to access this "
                        "resource."
                    )
                },
            )
            return HttpResponseForbidden(resp.render())

    host = req.get_host()
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        protocol = "http"
    else:
        protocol = "https"

    assignments = {
        group: [
            {
                "title": assignment.group_assignment.assignment.title,
                "due_date": assignment.group_assignment.due_date,
                "link": "{}://{}{}".format(
                    protocol,
                    host,
                    reverse(
                        "live",
                        kwargs={
                            "assignment_hash": assignment.group_assignment.hash,  # noqa
                            "token": token,
                        },
                    ),
                ),
                "results": assignment.get_results(),
            }
            for assignment in StudentAssignment.objects.filter(
                student=student, group_assignment__group=group
            )
        ]
        for group in student.groups.all()
    }

    assignments = {
        group: [
            {
                "title": assignment["title"],
                "due_date": assignment["due_date"],
                "link": assignment["link"],
                "results": assignment["results"],
                "done": assignment["results"]["n_second_answered"]
                == assignment["results"]["n"],
                "almost_expired": (
                    assignment["due_date"] - datetime.now(pytz.utc)
                )
                <= timedelta(days=3),
            }
            for assignment in assignments
        ]
        for group, assignments in assignments.items()
    }

    context = {
        "student": student,
        "groups": [
            {"title": group.title, "assignments": assignments[group]}
            for group in student.groups.all()
        ],
    }

    return render(req, "peerinst/student/index.html", context)


@require_http_methods(["POST"])
def leave_group(req):
    try:
        data = json.loads(req.body)
    except ValueError:
        logger.warning("The sent data wasn't in a valid JSON format.")
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Wrong data type was sent.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        username = data["username"]
        group_name = data["group_name"]
    except KeyError as e:
        logger.warning("The arguments '%s' were missing.", ",".join(e.args))
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        student = Student.objects.get(student__username=username)
    except Student.DoesNotExist:
        logger.warning(
            "There is no student corresponding to the username %s.", username
        )
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "The student doesn't seem to exist. Refresh the page and "
                    "try again"
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    try:
        group = StudentGroup.objects.get(name=group_name)
    except StudentGroup.DoesNotExist:
        logger.warning(
            "There is no group corresponding to the name %s.", group_name
        )
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "The group doesn't seem to exist. Refresh the page and "
                    "try again"
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    student.groups.remove(group)

    return HttpResponse()


@require_http_methods(["GET"])
def login_page(req):
    return render(req, "peerinst/student/login.html")


@require_http_methods(["POST"])
def send_signin_link(req):
    try:
        email = req.POST["email"]
    except KeyError as e:
        logger.warning("The arguments '%s' were missing.", ",".join(e.args))
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    student = Student.objects.filter(student__email=email)
    if student:
        if len(student) == 1:
            student = student[0]
        else:
            username, __ = get_student_username_and_password(email)
            student = student.filter(student__username=username).first()
        if student:
            student.student.is_active = True
            err = student.send_signin_email(req.get_host())
            if err is None:
                context = {}
            else:
                context = {"missing_student": True}
        else:
            context = {"missing_student": True}
    else:
        context = {"missing_student": True}

    return render(req, "peerinst/student/login_confirmation.html", context)
