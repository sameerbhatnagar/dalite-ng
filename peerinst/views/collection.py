# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import CreateView
from django.forms import HiddenInput, ModelForm
from ..models import Collection, Teacher
from ..mixins import LoginRequiredMixin, NoStudentsMixin


class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = [
            "title",
            "description",
            "image",
            "assignments",
            "discipline",
            "owner",
        ]
        widgets = {"owner": HiddenInput()}

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher")
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields["assignments"].queryset = teacher.assignments.all()
        self.fields["discipline"].queryset = teacher.disciplines.all()


class CollectionCreateView(LoginRequiredMixin, NoStudentsMixin, CreateView):

    template_name = "peerinst/collection/collection_form.html"
    form_class = CollectionForm

    def get_form_kwargs(self):
        kwargs = super(CollectionCreateView, self).get_form_kwargs()
        kwargs["teacher"] = Teacher.objects.get(user=self.request.user)
        return kwargs
