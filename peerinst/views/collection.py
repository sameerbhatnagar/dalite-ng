# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.core import serializers
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView
from django.forms import HiddenInput, ModelForm
from ..models import Collection, Teacher
from ..mixins import LoginRequiredMixin, NoStudentsMixin
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

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


class CollectionCreateView(LoginRequiredMixin, NoStudentsMixin, CreateView):

    template_name = "peerinst/collection/collection_form.html"
    form_class = CollectionForm

    def get_success_url(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return reverse("teacher", kwargs={"pk": teacher.pk})

    def get_form_kwargs(self):
        kwargs = super(CollectionCreateView, self).get_form_kwargs()
        kwargs["teacher"] = Teacher.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.owner=teacher
        return super(CollectionCreateView, self).form_valid(form)

class CollectionDetailView(LoginRequiredMixin, NoStudentsMixin, DetailView):
    model = Collection
    template_name = "peerinst/collection/collection_detail.html"

    def get_object(self):
        collection = get_object_or_404(self.model, pk=self.kwargs["collection_id"])
        return collection


class CollectionUpdateView(LoginRequiredMixin, NoStudentsMixin, UpdateView):
    model = Collection
    template_name = "peerinst/collection/collection_update.html"

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        collection.instance.owner = teacher
        return super(CollectionCreateView, self).edit_valid(form)

class CollectionListView(LoginRequiredMixin, NoStudentsMixin, ListView):

    model = Collection
    template_name = "peerinst/collection/collection_list.html"

    def get_object(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return teacher

    def get_queryset(self):
        return Collection.objects.filter(private=False)

class PersonalCollectionListView(LoginRequiredMixin, NoStudentsMixin, ListView):

    model = Collection
    template_name = "peerinst/collection/personal_collection_list.html"

    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return Collection.objects.filter(owner=teacher)

def featured_collections(request):
    data = serializers.serialize("json", Collection.objects.filter(featured=True))
    return JsonResponse(data, safe = False)
