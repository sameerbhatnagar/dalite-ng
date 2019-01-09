# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from tos.models import Consent

from ..models import (
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupMembership,
    StudentNotification,
)
from ..students import (
    authenticate_student,
    create_student_token,
    get_student_username_and_password,
)
from .decorators import student_required

logger = logging.getLogger("peerinst-views")


def validate_group_data(req):
    """
    Checks if the request is a well formed json, contains the data to get group
    information and the group exists.  The group is obtained with either a
    field `group_name` or `group_link`.

    Returns
    -------
    Either:
    StudentGroup
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

    if group_name is None:
        try:
            hash_ = re.match(
                r"^https?://[^/]+/\w{2}/live/signup/form/([0-9A-Za-z=_-]+)$",
                group_link,
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

    return group


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
        new_student = False
    else:
        user = authenticate_student(req, token)
        if isinstance(user, HttpResponse):
            return user

        if not user.is_active:
            user.is_active = True
            user.save()
            new_student = True
        else:
            new_student = False

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

    StudentNotification.clean(student)

    host = settings.ALLOWED_HOSTS[0]
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        protocol = "http"
        host = "{}:{}".format(host, settings.DEV_PORT)
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
            ).order_by("group_assignment__due_date")
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
            }
            for assignment in assignments
        ]
        for group, assignments in assignments.items()
    }

    if not Consent.objects.filter(
        user=student.student, tos__role__role="student"
    ).exists():
        return HttpResponseRedirect(
            reverse("tos:tos_consent", kwargs={"role": "student"})
            + "?next="
            + req.path
        )

    latest_student_consent = (
        Consent.objects.filter(
            user__username=student.student.username, tos__role="student"
        )
        .order_by("-datetime")
        .first()
    )

    data = {
        "expiry_blinking_delay": 3,
        "new_student": new_student,
        "student": {
            "username": student.student.username,
            "email": student.student.email,
            "member_since": student.student.date_joined.isoformat(),
            "tos": {
                "sharing": latest_student_consent.accepted,
                "signed_on": latest_student_consent.datetime.isoformat(),
            },
        },
        "groups": [
            {
                "name": group.group.name,
                "title": group.group.title,
                "notifications": group.send_emails,
                "member_of": group.current_member,
                "assignments": [
                    {
                        "title": assignment["title"],
                        "due_date": assignment["due_date"].isoformat(),
                        "link": assignment["link"],
                        "results": assignment["results"],
                    }
                    for assignment in assignments[group]
                ],
                "student_id": group.student_school_id,
                "student_id_needed": group.group.student_id_needed,
            }
            for group in groups
        ],
        "notifications": [
            {
                "link": notification.link,
                "icon": notification.notification.icon,
                "text": ugettext(notification.text),
                "pk": notification.pk,
            }
            for notification in student.notifications.order_by("-created_on")
        ],
        "urls": {
            "tos_modify": reverse(
                "tos:tos_modify", kwargs={"role": "student"}
            ),
            "remove_notification": reverse("student-remove-notification"),
            "remove_notifications": reverse("student-remove-notifications"),
            "join_group": reverse("student-join-group"),
            "leave_group": reverse("student-leave-group"),
            "save_student_id": reverse("student-change-id"),
            "student_toggle_group_notifications": reverse(
                "student-toggle-group-notifications"
            ),
        },
        "translations": {
            "assignment_about_to_expire": ugettext(
                "This assignment is about to expire"
            ),
            "assignment_expired": ugettext("Past due date"),
            "cancel": ugettext("Cancel"),
            "day": ugettext("day"),
            "days": ugettext("days"),
            "due_on": ugettext("Due on"),
            "expired": ugettext("Expired"),
            "go_to_assignment": ugettext("Go to assignment"),
            "hour": ugettext("hour"),
            "hours": ugettext("hours"),
            "leave": ugettext("Leave"),
            "leave_group_question": ugettext("Are you sure?"),
            "leave_group_text": ugettext(
                "This will remove you from the group. All your answers will "
                "be saved, but you won't appear as a member of the group to "
                "your teacher.  "
            ),
            "leave_group_title": ugettext("Leave group"),
            "minute": ugettext("minute"),
            "minutes": ugettext("minutes"),
            "n_questions_completed": ugettext("Number of questions completed"),
            "no_assignments": ugettext("No assignments yet"),
            "notifications_bell": ugettext(
                "Toggle email reminders for this group"
            ),
            "not_sharing": ugettext("Not sharing"),
            "sharing": ugettext("Sharing"),
            "student_id": ugettext("Student id"),
        },
    }

    context = {"data": json.dumps(data)}

    return render(req, "peerinst/student/index.html", context)


@student_required
@require_http_methods(["POST"])
def join_group(req, student):
    group = validate_group_data(req)
    if isinstance(group, HttpResponse):
        return group

    student.join_group(group, mail_type="new_group")

    try:
        membership = StudentGroupMembership.objects.get(
            student=student, group=group
        )
    except StudentGroupMembership.DoesNotExist:
        logger.warning(
            "Student {} isn't part of group {}.".format(student.pk, group.pk)
        )
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("You don't seem to be part of this group.")},
        )
        return HttpResponseBadRequest(resp.render())

    token = create_student_token(
        student.student.username, student.student.email
    )
    host = settings.ALLOWED_HOSTS[0]
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        protocol = "http"
        host = "{}:{}".format(host, settings.DEV_PORT)
    else:
        protocol = "https"

    data = {
        "name": group.name,
        "title": group.title,
        "notifications": membership.send_emails,
        "member_of": membership.current_member,
        "assignments": [
            {
                "title": assignment.group_assignment.assignment.title,
                "due_date": assignment.group_assignment.due_date.isoformat(),
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
            ).order_by("-group_assignment__due_date")
        ],
        "student_id": membership.student_school_id,
        "student_id_needed": group.student_id_needed,
    }

    return JsonResponse(data)


@student_required
@require_http_methods(["POST"])
def leave_group(req, student):
    group = validate_group_data(req)
    if isinstance(group, HttpResponse):
        return group

    student.leave_group(group)

    return HttpResponse()


@student_required
@require_http_methods(["POST"])
def toggle_group_notifications(req, student):
    group = validate_group_data(req)
    if isinstance(group, HttpResponse):
        return group

    membership = StudentGroupMembership.objects.get(
        student=student, group=group
    )

    notifications = not membership.send_emails

    membership.send_emails = notifications
    membership.save()

    return JsonResponse({"notifications": notifications})


@student_required
@require_http_methods(["POST"])
def remove_notification(req, student):
    """
    Removes the notification with the pk given as post value.

    Parameters
    ----------
    req : HttpRequest
        Request with post parameters:
            notification_pk : str
                Primary key of the notification
    student : Student
        Returned by @student_required (not used)

    Returns
    -------
    HttpResponse
        Empty 200 response if no errors or error response
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
        notification_pk = data["notification_pk"]
    except KeyError as e:
        logger.warning("The arguments '%s' were missing.", ",".join(e.args))
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        StudentNotification.objects.get(pk=notification_pk).delete()
    except StudentNotification.DoesNotExist:
        pass

    return HttpResponse()


@student_required
@require_http_methods(["POST"])
def remove_notifications(req, student):
    """
    Removes all notifications for the student.

    Parameters
    ----------
    req : HttpRequest
        Request
    student : Student
        Returned by @student_required

    Returns
    -------
    HttpResponse
        Empty 200 response if no errors or error response
    """
    StudentNotification.objects.filter(student=student).delete()

    return HttpResponse()


@student_required
@require_http_methods(["POST"])
def update_student_id(req, student):
    """
    Updates the student id.

    Parameters
    ----------
    req : HttpRequest
        Request with post parameters:
            student_id : str
                New student id
            group_name : str
                Name of the group (unique key)
    student : Student
        Student instance returned by @student_required

    Returns
    -------
    HttpResponse
        Empty 200 response if no errors or error response
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
        student_id = data["student_id"]
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
        group = StudentGroup.objects.get(name=group_name)
    except StudentGroup.DoesNotExist:
        logger.warning("Group {} doesn't exist.".format(group_name))
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("The wanted group doesn't seem to exist.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        membership = StudentGroupMembership.objects.get(
            student=student, group=group
        )
    except StudentGroupMembership.DoesNotExist:
        logger.warning(
            "Student {} isn't part of group {}.".format(student.pk, group.pk)
        )
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("You don't seem to be part of this group.")},
        )
        return HttpResponseBadRequest(resp.render())

    membership.student_school_id = student_id
    membership.save()
    logger.info(
        "Student id for student {} and group {} changed to {}.".format(
            student.pk, group.pk, student_id
        )
    )

    data = {"student_id": student_id}

    return JsonResponse(data)


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

    if not student:
        student, created = Student.get_or_create(email)
        print(created)
        logger.info("Student created with email {}.".format(email))

    elif len(student) == 1:
        student = student[0]

    else:
        username, __ = get_student_username_and_password(email)
        student = student.filter(student__username=username).first()

    if student:
        err = student.send_email(mail_type="signin")
        if err is None:
            context = {"error": False}
        else:
            context = {"error": True}

    return render(req, "peerinst/student/login_confirmation.html", context)


@student_required
@require_http_methods(["GET"])
def get_notifications(req, student):
    """
    Returns the notification data for the current student.

    Parameters
    ----------
    req ; HttpRequest
        Request
    student : Student
        Student instance returned by @student_required

    Returns
    -------
    HttpResponse
        Empty 200 response if no errors or error response
    """
    data = {
        "notifications": [
            {
                "link": notification.link,
                "icon": notification.notification.icon,
                "text": ugettext(notification.text),
                "pk": notification.pk,
            }
            for notification in student.notifications.order_by("-created_on")
        ],
        "urls": {
            "remove_notification": reverse("student-remove-notification"),
            "remove_notifications": reverse("student-remove-notifications"),
        },
    }
    return JsonResponse(data)
