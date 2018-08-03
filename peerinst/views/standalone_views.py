# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST, require_safe
from django.views.generic.edit import CreateView

from ..forms import EmailForm, StudentGroupAssignmentForm
from ..mixins import (
    LoginRequiredMixin,
    NoStudentsMixin,
)
from ..models import (
    Assignment,
    Question,
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupAssignment,
    Teacher,
)
from ..students import authenticate_student, verify_student_token
from ..util import get_object_or_none


def signup_through_link(request, group_hash):

    # Call logout to ensure a clean session
    logout(request)

    group = StudentGroup.get(group_hash)

    if group is None:
        raise Http404()
    else:
        if request.method == "POST":
            form = EmailForm(request.POST)
            if form.is_valid():

                # Get or create student
                student = Student.get_or_create(form.cleaned_data["email"])

                # Send confirmation e-mail
                student.send_confirmation_email(group, request.get_host())

                return TemplateResponse(
                    request,
                    "registration/sign_up_student_done.html",
                    context={"student": student, "group": group},
                )

        else:
            form = EmailForm()

        return TemplateResponse(
            request,
            "registration/sign_up_student.html",
            context={"form": form, "group": group},
        )


@require_safe
def confirm_signup_through_link(request, group_hash, token):

    # Call logout to ensure a clean session
    logout(request)

    # Validate token and activate account
    email, err = verify_student_token(token)
    group = StudentGroup.get(group_hash)

    if group is None:
        raise Http404()

    if email is not None:
        student = get_object_or_404(Student, student__email=email)
        student.student.is_active = True
        student.groups.add(group)
        student.save()

        return TemplateResponse(
            request, "registration/sign_up_student_confirmation.html", context={'group' : group}
        )
    else:
        raise PermissionDenied


@require_safe
def live(request, token, assignment_hash):

    # Call logout to ensure a clean session
    logout(request)

    # Login through token
    user = authenticate_student(token)
    login(request, user)

    # Get assignment for this token and current question
    group_assignment = StudentGroupAssignment.get(assignment_hash)
    student_assignment = StudentAssignment.get(
        student=user.student, group_assignment=group_assignment
    )

    # Redirect to view
    return HttpResponseRedirect(
        reverse(
            "question",
            kwargs={
                "assignment_id": student_assignment.group_assignment.assignment.pk,
                "question_id": student_assignment.get_current_question().id,
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


@login_required
@require_POST
def create_group_assignment(request, assignment_id):

    if request.is_ajax():
        form = StudentGroupAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return JsonResponse()
    else:
        # Bad request
        response = TemplateResponse(request, "400.html")
        return HttpResponseBadRequest(response.render())


class StudentGroupAssignmentCreateView(
    LoginRequiredMixin, NoStudentsMixin, CreateView
):
    """View to distribute an assignment to a group."""

    model = StudentGroupAssignment
    form_class = StudentGroupAssignmentForm

    def form_valid(self, form):
        # Create instance

        # Dispatch e-mails

        # Return to account
        pass

    def get_context_data(self, **kwargs):
        context = super(StudentGroupAssignmentCreateView, self).get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        context["assignment"] = get_object_or_404(Assignment, pk=self.kwargs["assignment_id"])
        context["teacher"] = teacher
        return context
