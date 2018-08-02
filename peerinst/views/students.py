# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.auth.backends import authenticate
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseUnauthorized,
)

from ..students import get_student_username_and_password, verify_token


def _get_student_info(req):
    try:
        token = req.GET["token"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There was a problem with your request.")},
        )
        return HttpResponseBadRequest(resp.render())

    email, err = verify_token(token)

    if err is not None:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "This page isn't valid. You can try asking for a new "
                    "login link."
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    username, password = get_student_username_and_password(email)

    return {"username": username, "email": email, "password": password}
