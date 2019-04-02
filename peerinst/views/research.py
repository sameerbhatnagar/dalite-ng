# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import string
from django.db.models import Count
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _

from ..mixins import student_check
from ..models import (
    Assignment,
    Answer,
    AnswerAnnotation,
    Discipline,
    Question,
    QuestionFlag,
    ShownRationale,
)


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
def research_index(request):
    template = "peerinst/research/index.html"
    context = {"disciplines": Discipline.objects.all()}
    return render(request, template, context)


def get_question_annotation_counts(discipline_title, annotator, assignment_id):
    """
    Returns:
    ========
    list of dicts, one for each question in discipline, and the counts of
    Answers and AnswerAnnotations for each
    """
    if discipline_title:
        questions_qs = Question.objects.filter(
            discipline__title=discipline_title
        )
    elif assignment_id:
        questions_qs = Assignment.objects.get(
            identifier=assignment_id
        ).questions.all()

    # FIXME:
    translation_table = string.maketrans("ABCDEFG", "1234567")

    question_annotation_counts = []
    for q in questions_qs:
        d1 = {}
        d1["question"] = q
        d1["total_annotations"] = AnswerAnnotation.objects.filter(
            score__isnull=False, answer__question_id=q.pk
        ).count()
        d1["total_annotations_by_user"] = AnswerAnnotation.objects.filter(
            score__isnull=False, answer__question_id=q.pk, annotator=annotator
        ).count()

        answer_frequencies = q.get_frequency_json("first_choice")
        for d2 in answer_frequencies:
            a_choice = d2["answer_label"][0].translate(translation_table)
            d2.update(
                {
                    "annotation_count": AnswerAnnotation.objects.filter(
                        score__isnull=False,
                        answer__question_id=q.pk,
                        answer__first_answer_choice=a_choice,
                    ).count(),
                    "annotation_count_by_user": AnswerAnnotation.objects.filter(  # noqa
                        score__isnull=False,
                        answer__question_id=q.pk,
                        answer__first_answer_choice=a_choice,
                        annotator=annotator,
                    ).count(),
                }
            )
        d1["answerchoices"] = answer_frequencies
        question_annotation_counts.append(d1)

    return question_annotation_counts


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
def research_discipline_question_index(
    request, discipline_title=None, assignment_id=None
):
    template = "peerinst/research/question_index.html"

    annotator = get_object_or_404(User, username=request.user)

    question_annotation_counts = get_question_annotation_counts(
        discipline_title=discipline_title,
        annotator=annotator,
        assignment_id=assignment_id,
    )

    context = {
        "questions": question_annotation_counts,
        "discipline_title": discipline_title,
        "assignment_id": assignment_id,
        "annotations_count": AnswerAnnotation.objects.filter(
            annotator=annotator, score__isnull=False
        ).count(),
        "annotator": annotator,
    }
    return render(request, template, context)


def research_question_answer_list(
    request,
    question_pk,
    answerchoice_value,
    discipline_title=None,
    assignment_id=None,
):
    template = "peerinst/research/answer_list.html"
    if discipline_title:
        reverse_url_name = "research-question-answer-list-by-discipline"
    elif assignment_id:
        reverse_url_name = "research-question-answer-list-by-assignment"

    annotator = get_object_or_404(User, username=request.user)
    if not annotator:
        logout(request)
        raise PermissionDenied

    # FIXME
    if answerchoice_value.isdigit():
        answerchoice_id = answerchoice_value
    else:
        answerchoice_id = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}[
            answerchoice_value
        ]

    answer_qs = Question.objects.get(pk=question_pk).answer_set.filter(
        question_id=question_pk, first_answer_choice=answerchoice_id
    )
    for a in answer_qs:
        annotation, created = AnswerAnnotation.objects.get_or_create(
            answer=a, annotator=annotator, score__isnull=True
        )
        if created:
            # need to drop null scored objects if scored ones exist
            if AnswerAnnotation.objects.filter(
                answer=a,
                annotator=annotator,
                answer__first_answer_choice=answerchoice_id,
                score__isnull=False,
            ).exists():
                annotation.delete()

    # only need two expert scores per rationale,
    # and those marked never show even by one person can be excluded
    already_scored = (
        AnswerAnnotation.objects.filter(
            answer__question_id=question_pk,
            score__isnull=False,
            answer__first_answer_choice=answerchoice_id,
        )
        .values("answer")
        .order_by("answer")
        .annotate(times_scored=Count("answer"))
        .filter(times_scored__gte=2)
        .values_list("answer__id", flat=True)
    )

    queryset = (
        AnswerAnnotation.objects.filter(
            answer__question_id=question_pk,
            annotator=annotator,
            answer__first_answer_choice=answerchoice_id,
        )
        .exclude(answer__id__in=already_scored)
        .annotate(times_shown=Count("answer__shown_answer"))
        .order_by("-times_shown")
    )

    AnswerAnnotationFormset = modelformset_factory(
        AnswerAnnotation, fields=("score",), extra=0
    )

    if request.method == "POST":
        formset = AnswerAnnotationFormset(request.POST)
        if formset.is_valid():
            instances = formset.save()

    formset = AnswerAnnotationFormset(queryset=queryset)

    context = {
        "formset": formset,
        "question": Question.objects.get(id=question_pk),
        "discipline_title": discipline_title,
        "question_pk": question_pk,
        "assignment_id": assignment_id,
        "annotations_count": AnswerAnnotation.objects.filter(
            annotator=annotator,
            score__isnull=False,
            answer__question_id=question_pk,
            answer__first_answer_choice=answerchoice_id,
        ).count(),
        "annotator": annotator,
    }
    return render(request, template, context)


def research_all_annotations_for_question(
    request, question_pk, discipline_title=None, assignment_id=None
):
    """
    Returns:
    ====================
    All answer annotations for a question, ordered for
    comparison by researchers
    """
    template = "peerinst/research/all_annotations.html"
    question = Question.objects.get(id=question_pk)
    context = {
        "question": question,
        "question_pk": question_pk,
        "discipline_title": discipline_title,
        "assignment_id": assignment_id,
    }

    all_annotations = []
    for label, answerchoice_text in question.get_choices():
        d1 = {}
        d1["answerchoice"] = label
        d1["annotations"] = []

        # FIXME
        if label.isdigit():
            answerchoice_id = label
        else:
            answerchoice_id = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}[
                label
            ]

        a_list = list(
            set(
                AnswerAnnotation.objects.filter(
                    score__isnull=False,
                    answer__question_id=question_pk,
                    answer__first_answer_choice=answerchoice_id,
                ).values_list("answer", flat=True)
            )
        )

        a_list.sort()

        for a in a_list:
            d2 = {}
            d2["answer"] = Answer.objects.get(pk=a)
            d2["scores"] = AnswerAnnotation.objects.filter(
                answer=a, score__isnull=False
            ).values("score", "annotator__username")
            d2["times_shown"] = ShownRationale.objects.filter(
                shown_answer=a
            ).count()
            d2["times_chosen"] = Answer.objects.filter(
                chosen_rationale_id=a
            ).count()
            d1["annotations"].append(d2)

        all_annotations.append(d1)

    context["all_annotations"] = all_annotations

    return render(request, template, context)


class QuestionFlagForm(ModelForm):
    class Meta:
        model = QuestionFlag
        fields = ["flag", "comment"]


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
def flag_question_form(
    request, question_pk, discipline_title=None, assignment_id=None
):
    """
    Get or Create QuestionFlag object for user, and allow edit
    """
    template = "peerinst/research/flag_question.html"
    user = get_object_or_404(User, username=request.user)
    question = get_object_or_404(Question, pk=question_pk)
    question_flag, created = QuestionFlag.objects.get_or_create(
        user=user, question=question
    )
    if not created:
        message = _(
            """
            Your input has already been forwarded to a myDALITE content
            moderator."
            """
        )

    if request.method == "POST":
        form = QuestionFlagForm(request.POST, instance=question_flag)
        if form.is_valid():
            instance = form.save()
            if instance.flag:
                message = _(
                    """
                    You have flagged this question, and your input
                    has been forwarded to a myDALITE content moderator.
                    """
                )
            else:
                message = _(
                    """
                    You have un-flagged this question, and thus it will be
                    it will be taken off the list of potentially problematic
                    questions.
                    """
                )
    elif created:
        message = None
    form = QuestionFlagForm(instance=question_flag)

    context = {
        "form": form,
        "question": question,
        "message": message,
        "discipline_title": discipline_title,
        "assignment_id": assignment_id,
    }

    return render(request, template, context)


def all_flagged_questions(request):
    """
    Return all flagged questions
    """

    template = "peerinst/research/all_flagged_questions.html"
    context = {"flags": QuestionFlag.objects.filter(flag=True)}

    return render(request, template, context)
