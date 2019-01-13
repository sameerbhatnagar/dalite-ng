# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from peerinst.models import Assignment, Question

from .decorators import teacher_required


@login_required
@require_http_methods(["POST"])
@teacher_required
def update_assignment_question_list(req):

    post_data = json.loads(req.body)

    try:
        question_id = post_data["question_id"]
        assignment_identifier = post_data["assignment_identifier"]
    except KeyError:
        return TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
            status=400,
        )

    try:
        assignment = Assignment.objects.get(identifier=assignment_identifier)
    except Assignment.DoesNotExist:
        return TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
            status=400,
        )

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
        return TemplateResponse(
            req,
            "400.html",
            context={"message": _("Some parameters are wrong.")},
            status=400,
        )

    if question in assignment.questions.all():
        assignment.questions.remove(question)
    else:
        assignment.questions.add(question)
    assignment.save()

    return HttpResponse("Success")
