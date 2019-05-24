# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_safe

from dalite.views.utils import get_json_params

from ..models import QUESTION_TYPES, Question
from .decorators import teacher_required

logger = logging.getLogger("peerinst-views")


@require_safe
@teacher_required
def teacher_page(req, teacher):
    """
    View that sends basic teacher page template skeleton.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    HttpResponse
        Html response with basic template skeleton
    """
    context = {"teacher": teacher}

    return render(req, "peerinst/teacher/page.html", context)


@require_POST
@teacher_required
def student_activity(req, teacher):
    """
    View that returns data on the teacher's student activity.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    pass


@require_POST
@teacher_required
def collections(req, teacher):
    """
    View that returns featured collections in the teacher's disciplines.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    pass


@require_POST
@teacher_required
def new_questions(req, teacher):
    """
    View that returns new questions in the teacher's disciplines.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """

    args = get_json_params(req, opt_args=["question_index", "n_questions"])
    if isinstance(args, HttpResponse):
        return args
    _, (question_index, n_questions) = args

    if question_index is None:
        question_index = 0
    if n_questions is None:
        n_questions = 10

    questions = Question.objects.filter(
        discipline__in=teacher.disciplines.all()
    ).order_by("-last_modified")[question_index : question_index + n_questions]

    data = {
        "questions": [
            {
                "author": question.user.username,
                "title": question.title,
                "text": question.text,
                "question_type": dict(QUESTION_TYPES)[question.type],
                "discipline": question.discipline.title,
                "last_modified": question.last_modified,
                "n_assignments": question.assignment_set.count(),
            }
            for question in questions
        ]
    }
    return JsonResponse(data)


@require_POST
@teacher_required
def saltise_message(req, teacher):
    """
    View that returns the current saltise message.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required` (not used)

    Returns
    -------
    JSONResponse
        Response with json data
    """
    pass


@require_POST
@teacher_required
def rationales_to_score(req, teacher):
    """
    View that returns a set of rationales to score in the teacher's
    disciplines.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    pass


@require_POST
@teacher_required
def messages(req, teacher):
    """
    View that returns the teacher's new messages.

    Parameters
    ----------
    req : HttpRequest
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    pass
