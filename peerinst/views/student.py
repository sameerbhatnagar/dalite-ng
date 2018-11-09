# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from ..models import (
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupMembership,
)
from ..students import (
    authenticate_student,
    create_student_token,
    get_student_username_and_password,
)

logger = logging.getLogger("peerinst-views")


def validate_student_group_data(req):
    """
    Checks if the request is a well formed json, contains the data to
    get student and group information and the student and group exist.
    The user is obtained with a field `username` and the group with
    either a field `group_name` or `group_link`.

    Returns
    -------
    Either:
    (Student, StudentGroup)
        Student and group corresponding for the request
    HttpResponse
        Response corresponding to the obtained error
    """
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
    except KeyError as e:
        logger.warning("The arguments '%s' were missing.", ",".join(e.args))
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        group_name = data["group_name"]
        group_link = None
    except KeyError:
        try:
            group_link = data["group_link"]
            group_name = None
        except KeyError:
            logger.warning(
                "The arguments 'group_name' or 'group_link' were missing."
            )
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

    if group_name is None:
        try:
            hash_ = re.match(
                r"live/signup/form/([0-9A-Za-z=_-]+)$", group_link
            ).group(1)
        except AttributeError:
            logger.warning(
                "A student signup was tried with the link %s.", group_link
            )
            resp = TemplateResponse(
                req,
                "400.html",
                context={
                    "message": _(
                        "There pas an error parsing the sent link. Please try "
                        "again."
                    )
                },
            )
            return HttpResponseBadRequest(resp.render())
        group = StudentGroup.get(hash_)
        if group is None:
            logger.warning(
                "There is no group corresponding to the hash %s.", hash_
            )
            resp = TemplateResponse(
                req,
                "400.html",
                context={
                    "message": _(
                        "There doesn't seem to be any group corresponding to"
                        "the link. Please try again."
                    )
                },
            )
            return HttpResponseBadRequest(resp.render())

    else:
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
                        "The group doesn't seem to exist. Refresh the page "
                        "and try again"
                    )
                },
            )
            return HttpResponseBadRequest(resp.render())

    return student, group


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

    groups = StudentGroupMembership.objects.filter(student=student)

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
                student=student, group_assignment__group=group.group
            )
        ]
        for group in groups
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
            {
                "name": group.group.name,
                "title": group.group.title,
                "notifications": group.sending_email,
                "member_of": group.current_member,
                "assignments": assignments[group],
            }
            for group in groups
        ],
        "notifications": student.notifications,
    }

    return render(req, "peerinst/student/index.html", context)


@require_http_methods(["POST"])
def join_group(req):
    result = validate_student_group_data(req)
    if isinstance(result, HttpResponse):
        return result
    else:
        student, group = result

    student.join_group(group)
    print(
        StudentGroupMembership.objects.filter(student=student, group=group)[
            0
        ].current_member
    )

    return HttpResponse()


@require_http_methods(["POST"])
def leave_group(req):
    result = validate_student_group_data(req)
    if isinstance(result, HttpResponse):
        return result
    else:
        student, group = result

    student.leave_group(group)

    return HttpResponse()


@require_http_methods(["POST"])
def toggle_group_notifications(req):
    result = validate_student_group_data(req)
    if isinstance(result, HttpResponse):
        return result
    else:
        student, group = result

    membership = StudentGroupMembership.objects.get(
        student=student, group=group
    )

    notifications = not membership.sending_email

    membership.sending_email = notifications
    membership.save()

    return JsonResponse({"notifications": notifications})


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
