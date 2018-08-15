# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import (
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

from peerinst.models import Assignment, Question

from .decorators import teacher_required


@login_required
@require_http_methods(["POST"])
@group_access_required
def update_assignment_question_list(req):
    try:
        question_id = req.POST["question_id"]
        assignment_identifier = req.POST["assignment_identifier"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render()), None
    try:
        assignment = Assignment.objects.get(identifier=assignment_identifier)
    except Assignment.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
        )
        return HttpResponseBadRequest(resp.render()), None

    if question in assignment.questions.all():
        assignment.questions.remove(question)
    else:
        assignment.questions.add(question)
    assignment.save()

    return HttpResponse()
