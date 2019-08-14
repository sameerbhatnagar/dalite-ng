# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.forms import ModelForm
from ..models import Collection, Teacher, Assignment, StudentGroup
from ..mixins import LoginRequiredMixin, NoStudentsMixin
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from peerinst.admin_views import get_assignment_aggregates
import collections
from dalite.views.utils import get_json_params
from .decorators import teacher_required
from django.views.decorators.http import require_POST


class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = [
            "title",
            "description",
            "image",
            "assignments",
            "discipline",
            "private",
        ]

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher")
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields["assignments"].queryset = teacher.assignments.all()
        self.fields["discipline"].queryset = teacher.disciplines.all()


class CollectionFormUpdate(ModelForm):
    class Meta:
        model = Collection
        fields = ["title", "description", "image", "discipline", "private"]


class CollectionCreateView(LoginRequiredMixin, NoStudentsMixin, CreateView):

    template_name = "peerinst/collection/collection_form.html"
    form_class = CollectionForm

    def get_success_url(self):
        return reverse("collection-update", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(CollectionCreateView, self).get_form_kwargs()
        kwargs["teacher"] = Teacher.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.owner = teacher
        return super(CollectionCreateView, self).form_valid(form)


class CollectionDetailView(LoginRequiredMixin, NoStudentsMixin, DetailView):
    model = Collection
    template_name = "peerinst/collection/collection_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        collection = self.get_object()
        context["collection_data"] = collection_data(collection=collection)
        context["assignment_data"] = {}
        for assignment in collection.assignments.all():
            context["assignment_data"][assignment.pk] = assignment_data(
                assignment=assignment
            )
        return context


def assignment_data(assignment):
    q_sums, q_students = get_assignment_aggregates(assignment=assignment)
    return q_sums


def collection_data(collection):
    assignments = collection.assignments.all()
    a_sums = collections.Counter(
        total_answers=0,
        correct_first_answers=0,
        correct_second_answers=0,
        switches=0,
    )
    for assignment in assignments:
        a_sums += assignment_data(assignment)
    return a_sums


class CollectionUpdateView(LoginRequiredMixin, NoStudentsMixin, UpdateView):
    form_class = CollectionFormUpdate
    template_name = "peerinst/collection/collection_update.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(owner=teacher)

    def get_success_url(self):
        return reverse("collection-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["teacher"] = get_object_or_404(Teacher, user=self.request.user)
        collection = self.get_object()
        teacher = get_object_or_404(Teacher, user=self.request.user)
        context["collection_assignments"] = collection.assignments.all()
        context["owned_assignments"] = Assignment.objects.filter(
            owner=self.request.user
        )
        context["followed_assignments"] = teacher.assignments.all().exclude(
            owner=self.request.user
        )
        return context


class CollectionDeleteView(LoginRequiredMixin, NoStudentsMixin, DeleteView):
    model = Collection
    template_name = "peerinst/collection/collection_delete.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(owner=teacher)

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.owner = teacher
        return super(CollectionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse("collection-list")


class CollectionListView(LoginRequiredMixin, NoStudentsMixin, ListView):

    model = Collection
    template_name = "peerinst/collection/collection_list.html"

    def get_queryset(self):
        return Collection.objects.filter(private=False)


class PersonalCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):

    model = Collection
    template_name = "peerinst/collection/personal_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(owner=teacher)


class FollowedCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):

    model = Collection
    template_name = "peerinst/collection/followed_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(followers=teacher)


class FeaturedCollectionListView(
    LoginRequiredMixin, NoStudentsMixin, ListView
):

    model = Collection
    template_name = "peerinst/collection/featured_collection_list.html"

    def get_queryset(self):
        return Collection.objects.filter(featured=True)


def featured_collections(request):
    data = serializers.serialize(
        "json", Collection.objects.filter(featured=True)
    )
    return JsonResponse(data, safe=False)


@teacher_required
@require_POST
def collection_add_assignment(request, teacher):
    args = get_json_params(request, args=["group_pk"])
    if isinstance(args, HttpResponse):
        return args
    (group_pk,), _ = args

    collection = Collection.objects.create(
        discipline=teacher.disciplines.get(id=1),
        owner=teacher,
        title="temporary title",
        description="temporary description",
    )
    student_group = get_object_or_404(StudentGroup, pk=group_pk)
    student_group_assignments = student_group.studentgroupassignment_set.all()
    for assignment in student_group_assignments:
        if assignment.assignment not in collection.assignments.all():
            collection.assignments.add(assignment.assignment)
            return JsonResponse({"pk": collection.pk})
