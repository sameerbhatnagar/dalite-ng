# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_safe

from ..models import Assignment, Question
from ..views import QuestionStartView


@require_safe
def live(request, token):

    # Validate token

    # Get StudentAssignment

    # Logout user then login using token

    # Get assignment for this token and current question

    # Redirect to view
    return HttpResponseRedirect(
        reverse(
            "question",
            kwargs={
                "assignment_id": assignment.pk,
                "question_id": question.id,
            },
        )
    )


@login_required
@require_safe
def navigate_assignment(request, assignment_id, question_id, direction):

    assignment = get_object_or_404(Assignment, identifier=assignment_id)
    question = get_object_or_404(Question, id=question_id)

    if question in assignment.questions.all():
        if direction == "next":
            # Get next question, wrap around if need be
            new_question = assignment.questions.order_by("?")[0]
        else:
            # Get previous question, wrap around if need be
            new_question = assignment.questions.order_by("?")[0]

        # Redirect
        return HttpResponseRedirect(
            reverse(
                "question",
                kwargs={
                    "assignment_id": assignment.pk,
                    "question_id": new_question.id,
                },
            )
        )
    else:
        raise Http404()
