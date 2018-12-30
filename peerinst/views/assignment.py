# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
import json

from peerinst.models import Assignment, Question

from .decorators import teacher_required

from django.core.exceptions import PermissionDenied


@login_required
@require_http_methods(["POST"])
@teacher_required
def update_assignment_question_list(req):

    post_data = json.loads(req.body)

    try:
        question_id = post_data["question_id"]
        assignment_identifier = post_data["assignment_identifier"]
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        assignment = Assignment.objects.get(identifier=assignment_identifier)
    except Assignment.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
        )
        return HttpResponseBadRequest(resp.render())

    # Check object permissions (to be refactored using mixin)
    if req.user in assignment.owner.all() or req.user.is_staff:
        # Check for student answers
        if assignment.answer_set.exclude(user_token__exact="").count() > 0:
            raise PermissionDenied
    else:
        raise PermissionDenied

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
        )
        return HttpResponseBadRequest(resp.render())

    if question in assignment.questions.all():
        assignment.questions.remove(question)
    else:
        assignment.questions.add(question)
    assignment.save()

    return HttpResponse("Success")
