# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from ..models import Student


def student_login_page(req):
    return render(req, "registration/student_login.html")


@require_http_methods(["POST"])
def student_send_signin_link(req):
    try:
        email = req.POST["email"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    try:
        student = Student.objects.get(student__email=email)
        student.student.is_active = True
        err = student.send_signin_email(req.get_host())
        if err is None:
            context = {}
        else:
            context = {"missing_student": True}
    except Student.DoesNotExist:
        context = {"missing_student": True}

    return render(req, "registration/student_login_confirmation.html", context)
