# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
from datetime import datetime
from itertools import chain
from operator import attrgetter

import pytz
from celery.result import AsyncResult
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.utils.translation import ugettext_lazy as translate
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_safe,
)
from pinax.forums.models import ForumThread

from dalite.views.errors import response_400, response_403, response_500
from dalite.views.utils import get_json_params

from ..gradebooks import convert_gradebook_to_csv
from ..models import (
    Answer,
    AnswerAnnotation,
    Collection,
    Question,
    RunningTask,
    StudentGroup,
    StudentGroupAssignment,
    TeacherNotification,
    UserMessage,
)
from ..rationale_annotation import choose_rationales_no_quality
from ..tasks import compute_gradebook_async
from .decorators import teacher_required

from ..util import get_student_activity_data


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

    data = {
        "urls": {
            "dalite_messages": reverse("teacher-dashboard--dalite-messages"),
            "remove_dalite_message": reverse(
                "teacher-dashboard--dalite-messages--remove"
            ),
            "saltise_image": static("peerinst/img/SALTISE-logo-icon.gif"),
            "rationales": reverse("teacher-dashboard--rationales"),
        }
    }
    student_activity_data, student_activity_json = get_student_activity_data(
        teacher, teacher.current_groups.all()
    )
    rationales = choose_rationales_no_quality(teacher, n=1)
    context = {
        "data": json.dumps(data),
        "question_list": Question.objects.filter(
            discipline__in=teacher.disciplines.all()
        ).order_by("?")[:1],
        "student_activity_data": student_activity_data,
        "student_activity_json": json.dumps(student_activity_json),
        "rationales": rationales,
    }

    return render(req, "peerinst/teacher/dashboard.html", context)


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


@require_GET
@teacher_required
def new_questions(req, teacher):
    """
    View that returns a question in the teacher's disciplines.

    Parameters
    ----------
    req : HttpRequest

    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    HttpResponse
    """
    questions = Question.objects.filter(
        discipline__in=teacher.disciplines.all()
    ).order_by("?")[:1]

    return TemplateResponse(
        req,
        "peerinst/question/cards/question_card.html",
        {"question_list": questions},
    )


@require_POST
@teacher_required
def dalite_messages(req, teacher):
    """
    View that returns the current dalite messages.

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
    messages = [
        {
            "id": message.id,
            "title": message.message.title,
            "text": message.message.text,
            "colour": message.message.type.colour,
            "removable": message.message.type.removable,
            "link": message.message.link,
            "authors": [
                {
                    "name": author.name,
                    "picture": author.picture.url
                    if author.picture.name
                    else "",
                }
                for author in message.message.authors.all()
            ],
        }
        for message in UserMessage.objects.filter(user=teacher.user)
        if (
            message.message.start_date is None
            or message.message.start_date <= datetime.now(pytz.utc)
        )
        and (
            message.message.end_date is None
            or message.message.end_date >= datetime.now(pytz.utc)
        )
        and message.showing
    ]
    data = {"messages": messages}
    return JsonResponse(data)


@require_POST
@teacher_required
def remove_dalite_message(req, teacher):
    args = get_json_params(req, args=["id"])
    if isinstance(args, HttpResponse):
        return args
    (id_,), _ = args
    try:
        message = UserMessage.objects.get(pk=id_)
        message.showing = False
        message.save()
    except UserMessage.DoesNotExist:
        pass
    return HttpResponse("")


@require_GET
@teacher_required
def rationales_to_score(req, teacher):
    """
    View that returns one rationale to score.

    Parameters
    ----------
    req : HttpRequest

    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    HttpResponse
    """
    rationales = choose_rationales_no_quality(teacher, n=1)

    return TemplateResponse(
        req,
        "peerinst/teacher/cards/rationale_to_score_card.html",
        {"rationales": rationales},
    )


@require_GET
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
    threads = list(
        sorted(
            (s.thread for s in teacher.user.forum_subscriptions.iterator()),
            key=attrgetter("last_reply"),
            reverse=True,
        )
    )
    notification_type = ContentType.objects.get(
        app_label="pinax_forums", model="ThreadSubscription"
    )
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
                "n_new": TeacherNotification.objects.filter(
                    teacher=teacher, notification_type=notification_type
                ).count(),
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
def mark_message_read(req, teacher):
    """
    Unsubscribes the `teacher` from a thread (won't appear in the messages).

    Parameters
    ----------
    req : HttpRequest
        Request with:
            optional parameters:
                id: int
                    Thread primary key
    teacher : Teacher
        Teacher instance returned by `teacher_required`

    Returns
    -------
    HttpResponse
        Error response or empty 200 response
    """
    args = get_json_params(req, opt_args=["id"])
    if isinstance(args, HttpResponse):
        return args
    _, (id_,) = args

    notification_type = ContentType.objects.get(
        app_label="pinax_forums", model="ThreadSubscription"
    )

    if id_ is None:
        TeacherNotification.objects.filter(
            teacher=teacher, notification_type=notification_type
        ).delete()
    else:
        TeacherNotification.objects.filter(
            teacher=teacher, notification_type=notification_type, object_id=id_
        ).delete()

    return HttpResponse("")


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
    id_ = req.POST.get("id")
    score = int(req.POST.get("score"))

    if score not in range(0, 4):
        return response_400(
            req,
            msg=translate("The score wasn't in a valid range."),
            logger_msg=("The score wasn't valid; was {}.".format(score)),
            log=logger.warning,
        )

    if score == 0:
        # Flag as inappropriate
        pass
    else:
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

    return redirect(reverse("teacher-dashboard--rationales"))


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
