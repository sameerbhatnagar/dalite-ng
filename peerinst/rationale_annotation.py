# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

from quality.models import Quality

from .models import Answer, AnswerAnnotation, Teacher


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
