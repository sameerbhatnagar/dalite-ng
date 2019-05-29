# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from datetime import datetime

import pytz
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as translate
from django.views.decorators.http import require_POST, require_safe

from dalite.views.errors import response_400
from dalite.views.utils import get_json_params

from ..models import (
    QUESTION_TYPES,
    Answer,
    AnswerAnnotation,
    Question,
    StudentGroupMembership,
)
from ..rationale_annotation import choose_rationales
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
    teacher.last_page_access = datetime.now(pytz.utc)
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
        Response with json data:
            {
                groups: [{
                    title: str
                        Group title
                    n_students: int
                        Number of students in the group
                    new: bool
                        If there is any new activity in the group
                    assignments: [{
                        title: str
                            Title of the assignment
                        n_completed: int
                            Number of students having completed the assignment
                        mean_grade: float
                            Average grade on the assignment
                        min_grade: float
                            Minimum grade on the assignment
                        max_grade: float
                            Maximum grade on the assignment
                        new: bool
                            If the information changed since last login
                        expired: bool
                            If the assignment has expired
                        link: str
                            Link to the assignment
                    }]
                }]
            }
    """
    host = settings.ALLOWED_HOSTS[0]
    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        protocol = "http"
        host = "{}:{}".format(host, settings.DEV_PORT)
    else:
        protocol = "https"

    assignments = [
        {
            "title": group.title,
            "n_students": StudentGroupMembership.objects.filter(
                group=group
            ).count(),
            "assignments": [
                {
                    "title": assignment.assignment.title,
                    "new": assignment.last_modified > teacher.last_page_access
                    if teacher.last_page_access
                    else True,
                    "expired": assignment.expired,
                    "link": "{}://{}{}".format(
                        protocol, host, assignment.link
                    ),
                    "results": [
                        (a.completed, a.grade)
                        for a in assignment.studentassignment_set.iterator()
                    ],
                }
                for assignment in group.studentgroupassignment_set.iterator()
            ],
        }
        for group in teacher.current_groups.iterator()
    ]

    data = {
        "groups": [
            {
                "title": group["title"],
                "n_students": group["n_students"],
                "new": any(a["new"] for a in group["assignments"]),
                "assignments": [
                    {
                        "title": assignment["title"],
                        "n_completed": sum(
                            a[0] for a in assignment["results"]
                        ),
                        "mean_grade": float(
                            sum(a[1] for a in assignment["results"] if a[0])
                        )
                        / sum(a[0] for a in assignment["results"])
                        if group["n_students"]
                        and any(a[0] for a in assignment["results"])
                        else 0,
                        "min_grade": min(
                            a[1] for a in assignment["results"] if a[0]
                        )
                        if group["n_students"]
                        and any(a[0] for a in assignment["results"])
                        else 0,
                        "max_grade": max(
                            a[1] for a in assignment["results"] if a[0]
                        )
                        if group["n_students"]
                        and any(a[0] for a in assignment["results"])
                        else 0,
                        "new": assignment["new"],
                        "expired": assignment["expired"],
                        "link": assignment["link"],
                    }
                    for assignment in group["assignments"]
                ],
            }
            for group in assignments
        ]
    }

    return JsonResponse(data)


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
        Request with:
            optional parameters:
                n: int (default : 10)
                    Number of questions to return
                current: List[int] (default : [])
                    Primary keys of current questions (not to return)
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data:
            {
                questions: [{
                    author: str
                        Author username
                    discipline: str
                        Discipline of the question
                    last_modified: %Y-%m-%dT%H:%M:%S.%fZ
                        Datetime of last modification
                    n_assignment: int
                        Number of assignments containing the question
                    text: str
                        Full question text
                    title: str
                        Question title
                }]
            }
    """

    args = get_json_params(req, opt_args=["n", "current"])
    if isinstance(args, HttpResponse):
        return args
    _, (n, current) = args

    if n is None:
        n = 10
    if current is None:
        current = []

    questions = (
        Question.objects.filter(discipline__in=teacher.disciplines.all())
        .exclude(pk__in=current)
        .order_by("-last_modified")[:n]
    )

    data = {
        "questions": [
            {
                "author": question.user.username,
                "discipline": question.discipline.title,
                "last_modified": question.last_modified,
                "n_assignments": question.assignment_set.count(),
                "question_type": dict(QUESTION_TYPES)[question.type],
                "text": question.text,
                "title": question.title,
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
        Request with:
            optional parameters:
                n: int (default : 5)
                    Number of rationales to return
                current: List[int] (default : [])
                    Primary keys of current rationales (not to return)
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    args = get_json_params(req, opt_args=["n", "current"])
    if isinstance(args, HttpResponse):
        return args
    _, (n, current) = args

    if n is None:
        n = 5
    if current is None:
        current = []

    rationales = choose_rationales(teacher, n=n + len(current))
    rationales = [a for a in rationales if a.pk not in current]

    data = {
        "rationales": [
            {
                "id": answer.id,
                "title": answer.question.title,
                "rationale": answer.rationale,
                "choice": answer.first_answer_choice,
                "text": answer.question.answerchoice_set.all()[
                    answer.first_answer_choice - 1
                ].text,
                "correct": answer.question.is_correct(
                    answer.first_answer_choice
                ),
            }
            for answer in rationales
        ]
    }

    return JsonResponse(data)


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


@require_POST
@teacher_required
def evaluate_rationale(req, teacher):
    """
    Add the `teacher`'s evaluation for a rationale.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                id: int
                    Primary key of the rationale
                score: int
                    Given score
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JSONResponse
        Response with json data
    """
    args = get_json_params(req, args=["id", "score"])
    if isinstance(args, HttpResponse):
        return args
    (id_, score), _ = args

    if score not in range(4):
        return response_400(
            req,
            msg=translate("The score wasn't in a valid range."),
            logger_msg=("The score wasn't valid; was {}.".format(score)),
            log=logger.warning,
        )

    try:
        answer = Answer.objects.get(id=id_)
    except Answer.DoesNotExist:
        return response_400(
            req,
            msg=translate("Unkown answer id sent."),
            logger_msg=("No answer could be found for pk {}.".format(id_)),
            log=logger.warning,
        )

    AnswerAnnotation.objects.create(
        answer=answer, annotator=teacher.user, score=score
    )

    return HttpResponse("")
