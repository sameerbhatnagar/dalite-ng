# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import CreateView
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
