# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from django.db.models import Count, F, Q

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
    from .util import student_list_from_student_groups

    # if teacher has active students, sample from their most recent student
    # answers
    current_assignments = teacher.current_groups.values_list(
        "studentgroupassignment__assignment__identifier", flat=True
    )
    current_students = student_list_from_student_groups(
        teacher.current_groups.all().values_list("pk", flat=True)
    )
    _answers = Answer.objects.filter(
        user_token__in=current_students, assignment_id__in=current_assignments
    ).order_by("datetime_second")

    print(_answers.count())
    print(_answers)

    # if not, sample from answers of previously active students

    # if not, sample from answers to favourite_questions

    # if still nothing, sample from most popular answers in teacher disciplines

    # if no teacher discipline, get most popular answers amongst students

    # remove answers that have been scored twice already, or that
    # have been scored by the current users

    q_list = list(teacher.favourite_questions.all())
    for a in teacher.assignments.all():
        q_list.extend(list(a.questions.all().values_list("pk", flat=True)))
    q_list = list(set(q_list))

    convincing = Answer.objects.filter(
        chosen_rationale__isnull=False
    ).values_list("chosen_rationale", flat=True)

    no_score_needed = (
        AnswerAnnotation.objects.annotate(times_scored=Count("answer"))
        .filter(
            Q(times_scored__gt=2)
            | Q(annotator=teacher.user)
            | Q(score__isnull=False)
        )
        .values_list("answer", flat=True)
    )

    if convincing:
        answers = (
            Answer.objects.filter(
                Q(question__discipline__in=teacher.disciplines.all())
                | Q(question_id__in=q_list)
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
                Q(question__discipline__in=teacher.disciplines.all())
                | Q(question_id__in=q_list)
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
