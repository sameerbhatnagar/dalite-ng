# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from datetime import datetime
from itertools import chain

import pytz
from celery.result import AsyncResult
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as translate
from django.views.decorators.http import require_POST, require_safe
from pinax.forums.models import ForumThread

from dalite.views.errors import response_400, response_403, response_500
from dalite.views.utils import get_json_params

from ..gradebooks import convert_gradebook_to_csv
from ..models import (
    QUESTION_TYPES,
    Answer,
    AnswerAnnotation,
    Collection,
    Question,
    RunningTask,
    StudentGroup,
    StudentGroupAssignment,
    StudentGroupMembership,
)
from ..rationale_annotation import choose_rationales
from ..tasks import compute_gradebook_async
from .decorators import teacher_required

logger = logging.getLogger("peerinst-views")


@require_safe
@teacher_required
def dashboard(req, teacher):
    """
    View that sends basic teacher dashboard template skeleton.

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
    teacher.last_dashboard_access = datetime.now(pytz.utc)

    data = {"urls": {"collections": reverse("teacher-dashboard--collections")}}
    context = {"data": json.dumps(data)}

    return render(req, "peerinst/teacher/dashboard.html", context)


@require_POST
@teacher_required
def student_activity(req, teacher):
    """
    View that returns data on the teacher's student activity.
        Request
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JsonResponse
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
                    "new": assignment.last_modified
                    > teacher.last_dashboard_access
                    if teacher.last_dashboard_access
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
        Request with:
            optional parameters:
                n: int (default : 5)
                    Number of questions to return
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    JsonResponse
        Response with json data:
            {
                "collections": [
                    {
                        title : str
                            Collection title
                        discipline : str
                            Collection discipline
                        n_assignments : int
                            Number of assignments in collection
                        n_followers : str
                            Number of followers for the collection
                    }
                ]
            }
    """
    args = get_json_params(req, opt_args=["n"])
    if isinstance(args, HttpResponse):
        return args
    _, (n,) = args

    if n is None:
        n = 5

    data = {
        "collections": [
            {
                "title": collection.title,
                "description": collection.description,
                "discipline": collection.discipline.title,
                "n_assignments": collection.assignments.count(),
                "n_followers": collection.n_followers,
            }
            for collection in Collection.objects.filter(
                discipline__in=teacher.disciplines.all()
            )
            .annotate(n_followers=models.Count("followers"))
            .order_by("-n_followers")
            .all()[:n]
        ]
    }
    return JsonResponse(data)


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
    JsonResponse
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
    JsonResponse
        Response with json data {
            message: Optional[str]
                Message to show
            link: Optional[str]
                Link to go to when clicked
        }
    """
    data = {"message": None, "link": None}
    return JsonResponse(data)


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
    JsonResponse
        Response with json data: {
            rationales: [
                {
                    id : int
                        Id the answer
                    title : str
                        Title of the question
                    rationale : str
                        Rationale of the answer
                    choice : int
                        Index of the answer choice
                    text : string
                        Text of the answer choice
                    correct : bool
                        If the answer choice is correct or not
                }
            ]
        }
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
    JsonResponse
        Response with json data
            {
                threads: [{
                    if: int
                        Primary key of the thread
                    title: str
                        Title of the thread
                    last_reply: {
                        author: str
                            Author of the post
                        content: str
                            Text of the post
                    }
                    n_new: int
                        Number of new replies since last visit of dashboard
                    link: str
                        Link to the thread in forums
                }]
            }
    """
    threads = [s.thread for s in teacher.user.forum_subscriptions.iterator()]
    last_replies = [thread.last_reply for thread in threads]
    data = {
        "threads": [
            {
                "id": thread.pk,
                "title": thread.title,
                "last_reply": {
                    "author": last_reply.author.username,
                    "content": last_reply.content,
                },
                "n_new": thread.replies.filter(
                    created__gt=teacher.last_dashboard_access
                ).count()
                if teacher.last_dashboard_access is not None
                else thread.replies.count(),
                "link": reverse(
                    "pinax_forums:thread", kwargs={"pk": thread.pk}
                ),
            }
            for thread, last_reply in zip(threads, last_replies)
        ]
    }
    return JsonResponse(data)


@require_POST
@teacher_required
def unsubscribe_from_thread(req, teacher):
    """
    Unsubscribes the `teacher` from a thread (won't appear in the messages).

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                id: int
                    Thread primary key
                score: int
                    Given score
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    HttpResponse
        Error response or empty 200 response
    """
    args = get_json_params(req, args=["id"])
    if isinstance(args, HttpResponse):
        return args
    (id_,), _ = args
    try:
        thread = ForumThread.objects.get(pk=id_)
    except ForumThread.DoesNotExist:
        return response_400(
            req,
            msg=translate("The thread couldn't be found."),
            logger_msg=(
                "The thread with pk {} couldn't be found.".format(id_)
            ),
            log=logger.warning,
        )

    thread.subscriptions.filter(user=teacher.user).delete()

    return HttpResponse("")


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
    HttpResponse
        Error response or empty 200 response
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


@require_POST
@teacher_required
def request_gradebook(req, teacher):
    """
    Request the generation of a gradebook. An response containing the task id
    is returned so the client can poll the server for the result until it's
    ready.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters
                group_id: int
                    Primary key of the group for which the gradebook is wanted
            optional parameters:
                assignment_id: int (default : None)
                    Primary key of the assignment for which the gradebook is
                    wanted
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    Either
        JsonResponse with json data
            Response 201 (created) with json data if computation run
            asynchronously
                {
                    task_id: str
                        Id corresponding to the celery task for use in polling
                }
            Response 200 with json data if computation run synchronously
                Either
                    If group gradebook wanted
                        {
                            assignments: List[str]
                                Assignment identifier
                            school_id_needed: bool
                                If a school id is needed
                            results: [{
                                school_id: Optional[str]
                                    School id if needed
                                email: str
                                    Student email
                                assignments: [{
                                    n_completed: int
                                        Number of completed questions
                                    n_correct: int
                                        Number of correct questions
                                }]
                            }]
                        }
                    If assignment gradebook wanted
                        {
                            questions: List[str]
                                Question title
                            school_id_needed: bool
                                If a school id is needed
                            results: [{
                                school_id: Optional[str]
                                    School id if needed
                                email: str
                                    Student email
                                questions: List[float]
                                    Grade for each question
                            }]
                        }
        HttpResponse
            Error response
    """
    args = get_json_params(req, args=["group_id"], opt_args=["assignment_id"])
    if isinstance(args, HttpResponse):
        return args
    (group_pk,), (assignment_pk,) = args

    try:
        group = StudentGroup.objects.get(pk=group_pk)
    except StudentGroup.DoesNotExist:
        return response_400(
            req,
            msg=translate("The group doesn't exist."),
            logger_msg=(
                "Access to {} with an invalid group {}.".format(
                    req.path, group_pk
                )
            ),
            log=logger.warning,
        )

    if teacher not in group.teacher.all():
        return response_403(
            req,
            msg=translate(
                "You don't have access to this resource. You must be "
                "registered as a teacher for the group."
            ),
            logger_msg=(
                "Unauthorized access to group {} from teacher {}.".format(
                    group.pk, teacher.pk
                )
            ),
            log=logger.warning,
        )

    if assignment_pk is not None:
        try:
            assignment = StudentGroupAssignment.objects.get(pk=assignment_pk)
        except StudentGroupAssignment.DoesNotExist:
            return response_400(
                req,
                msg=translate("The group or assignment don't exist."),
                logger_msg=(
                    "Access to {} with an invalid assignment {}.".format(
                        req.path, assignment_pk
                    )
                ),
                log=logger.warning,
            )

    result = compute_gradebook_async(group_pk, assignment_pk)

    if assignment_pk is None:
        description = "gradebook for group {}".format(group.name)
    else:
        description = "gradebook for assignment {} and group {}".format(
            assignment.assignment.identifier, group.name
        )

    if isinstance(result, AsyncResult):
        task = RunningTask.objects.create(
            id=result.id, description=description, teacher=teacher
        )
        data = {
            "id": task.id,
            "description": task.description,
            "completed": False,
            "datetime": task.datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        return JsonResponse(data, status=201)
    else:
        return download_gradebook(req, results=result)


@require_POST
@teacher_required
def get_gradebook_task_result(req, teacher):
    """
    Returns a 200 response if the gradebook is ready. If not, will return a 202
    response.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                task_id: str
                    Id of the celery task responsible for the gradebook
                    generation sent with the first request for a gradebook
    teacher : Teacher
        Teacher instance returned by `teacher_required` (not used)

    Returns
    -------
    HttpResponse
        Either
            Empty 200 response (task done)
            Empty 202 response (accepted, still processing)
            Empty 500 response (error)
    """
    args = get_json_params(req, args=["task_id"])
    if isinstance(args, HttpResponse):
        return args
    (task_id,), _ = args

    result = AsyncResult(task_id)

    try:
        if result.ready():
            return HttpResponse("", status=200)
        else:
            return HttpResponse("", status=202)
    except AttributeError:
        return response_500(
            req,
            msg="",
            logger_msg="Error computing gradebook for teacher {}".format(
                teacher.user.username
            )
            + " and task {}.".format(task_id),
            log=logger.warning,
            use_template=False,
        )


@require_POST
@teacher_required
def remove_gradebook_task(req, teacher):
    """
    Removes the failed gradebook task from the running tasks.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                task_id: str
                    Id of the celery task responsible for the gradebook
                    generation sent with the first request for a gradebook
    teacher : Teacher
        Teacher instance returned by `teacher_required` (not used)

    Returns
    -------
    HttpResponse
        Empty 200 response
    """
    args = get_json_params(req, args=["task_id"])
    if isinstance(args, HttpResponse):
        return args
    (task_id,), _ = args

    try:
        task = RunningTask.objects.get(id=task_id)
    except RunningTask.DoesNotExist:
        return HttpResponse("")

    task.delete()
    return HttpResponse("")


@require_safe
@teacher_required
def get_tasks(req, teacher):
    tasks = [
        {
            "id": task.id,
            "description": task.description,
            "completed": AsyncResult(task.id).ready(),
            "datetime": task.datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        for task in RunningTask.objects.filter(teacher=teacher).order_by(
            "-datetime"
        )
    ]

    data = {"tasks": tasks}

    return JsonResponse(data)


@require_POST
@teacher_required
def download_gradebook(req, teacher, results=None):
    """
    Download the wanted gradebook.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                task_id: str
                    Id of the celery task responsible for the gradebook
                    generation sent with the first request for a gradebook
    teacher : Teacher
        Teacher instance returned by `teacher_required` (not used)
    results : Optional[Dict[str, Any]]
        Either
            If group gradebook
                {
                    group: str
                        Title of the group
                    assignments: List[str]
                        Assignment identifier
                    school_id_needed: bool
                        If a school id is needed
                    results: [{
                        school_id: Optional[str]
                            School id if needed
                        email: str
                            Student email
                        assignments: [{
                            n_completed: Optional[int]
                                Number of completed questions
                            n_correct: Optional[int]
                                Number of correct questions
                        }]
                    }]
                }
            If assignment gradebook
                {
                    group: str
                        Title of the group
                    assignment: str
                        Title of the assignment
                    questions: List[str]
                        Question title
                    school_id_needed: bool
                        If a school id is needed
                    results: [{
                        school_id: Optional[str]
                            School id if needed
                        email: str
                            Student email
                        questions: List[Optional[float]]
                            Grade for each question
                    }]
                }

    Returns
    -------
    StreamingHttpResponse
        csv file with the gradebook results
    """
    if results is None:
        args = get_json_params(req, args=["task_id"])
        if isinstance(args, HttpResponse):
            return args
        (task_id,), _ = args

        result = AsyncResult(task_id)

        try:
            if not result.ready():
                return response_400(
                    req,
                    msg="The gradebook isn't ready.",
                    logger_msg="Not completed gradebook {}".format(task_id)
                    + " accessed by teacher {}".format(teacher.user.username),
                )
        except AttributeError:
            return response_500(
                req,
                msg="There is no gradebook corresponding to this url. "
                "Please ask for a new one.",
                logger_msg="Celery error getting gradebook"
                " for teacher {}".format(teacher.user.username)
                + " and task {}.".format(task_id),
                log=logger.warning,
                use_template=False,
            )

        results = result.result

        if RunningTask.objects.filter(id=task_id):
            RunningTask.objects.get(id=task_id).delete()

    if "assignment" in results:
        filename = "myDALITE_gradebook_{}_{}.csv".format(
            results["group"], results["assignment"]
        )
    else:
        filename = "myDALITE_gradebook_{}.csv".format(results["group"])
    gradebook_gen = convert_gradebook_to_csv(results)
    data = chain(iter((filename + "\n",)), gradebook_gen)
    resp = StreamingHttpResponse(data, content_type="text/csv")
    return resp
