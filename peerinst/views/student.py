# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from ..models import Student
from ..students import authenticate_student


@require_http_methods(["GET"])
def student_page(req, token=None):
    """
    Main student page. Accessed through a link sent by email containing
    a token or without the token for a logged in student.
    """

    # get student from token or from logged in user
    if token is None:
        if not isinstance(req.user, User):
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
    else:
        user = authenticate_student(req, token)
        if isinstance(user, HttpResponse):
            return user
        logout(req)
        login(req, user)
        try:
            student = Student.objects.get(student=user)
        except Student.DoesNotExist:
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

    context = {"student": student}

    return render(req, "peerinst/student/index.html", context)
