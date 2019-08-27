# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from django.db.models import F, Count

from quality.models import Quality

from .models import Answer, AnswerAnnotation, Question, Teacher


def choose_questions(teacher):
    """
    Selects subset of questions that are relevant to teacher interests
    """

    question_list = Question.unflagged_objects.all().order_by("-created_on")

    if len(teacher.disciplines.all()) > 0:
        question_list = question_list.filter(
            discipline__in=teacher.disciplines.all()
        ).exclude(teacher=teacher)
    if len(teacher.favourite_questions.all()) > 0:
        question_list = question_list.exclude(
            pk__in=teacher.favourite_questions.all()
        )
    return question_list


def choose_rationales(teacher, n=5):
    """
    Evaluates each rationale based on if the `teacher` should evaluate and
    returns the top `n` ones.

    Parameters
    ----------
    teacher : Teacher
        Teacher for whom the rationales should be chosen
    n : int (default : 5)
        Number of answers to return

    Returns
    -------
    List[Answer]
        Rationales for the teacher to evaluate
    """
    assert isinstance(teacher, Teacher), "Precondition failed for `teacher`"
    assert isinstance(n, int), "Precondition failed for `n`"

    answers = (
        Answer.objects.filter(
            question__discipline__in=teacher.disciplines.all()
        )
        .exclude(
            pk__in=AnswerAnnotation.objects.filter(
                annotator=teacher.user
            ).values_list("answer", flat=True)
        )
        .order_by("-datetime_first")
    )

    if not answers:
        return []

    if Quality.objects.filter(
        quality_type__type="global", quality_use_type__type="validation"
    ).exists():
        qualities = map(
            itemgetter(0),
            Quality.objects.get(
                quality_type__type="global",
                quality_use_type__type="validation",
            ).batch_evaluate(answers),
        )
        answers = [
            a
            for a, q in sorted(
                zip(answers, qualities), key=itemgetter(1), reverse=True
            )
        ]

    return answers[:n]


def choose_rationales_no_quality(teacher, n=5):
    """
    Evaluates each rationale based on if the `teacher` should evaluate and
    returns the top `n` ones.
    Filters for actual student answers that have resulted in students
    changing their mind, and ordered by those that have been shown often

    Parameters
    ----------
    teacher : Teacher
        Teacher for whom the rationales should be chosen
    n : int (default : 5)
        Number of answers to return

    Returns
    -------
    List[Answer]
        Rationales for the teacher to evaluate
    """
    assert isinstance(teacher, Teacher), "Precondition failed for `teacher`"
    assert isinstance(n, int), "Precondition failed for `n`"

    q_list = list(teacher.favourite_questions.all())
    for a in teacher.assignments.all():
        q_list.extend(list(a.questions.all().values_list("pk", flat=True)))
    q_list = list(set(q_list))

    convincing = Answer.objects.filter(
        chosen_rationale__isnull=False
    ).values_list("chosen_rationale", flat=True)

    no_score_needed = (
        AnswerAnnotation.objects.exclude(score__isnull=True)
        .annotate(times_scored=Count("answer"))
        .filter(times_scored__lte=2)
        .exclude(annotator=teacher.user)
        .values_list("answer", flat=True)
    )

    if convincing:
        answers = (
            Answer.objects.filter(
                question__discipline__in=teacher.disciplines.all(),
                question_id__in=q_list,
            )
            .exclude(second_answer_choice__isnull=True)
            .filter(pk__in=convincing)
            .exclude(pk__in=no_score_needed)
            .annotate(times_shown=Count("shown_answer"))
            .order_by("-times_shown")
        )
    else:
        answers = (
            Answer.objects.filter(
                question__discipline__in=teacher.disciplines.all(),
                question_id__in=q_list,
            )
            .exclude(second_answer_choice__isnull=True)
            .exclude(first_answer_choice=F("second_answer_choice"))
            .exclude(pk__in=no_score_needed)
            .annotate(times_shown=Count("shown_answer"))
            .order_by("-times_shown")
        )

    if not answers:
        return []
    else:
        return answers[:n]
