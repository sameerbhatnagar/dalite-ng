# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


def edit_patterns():
    return [
        url(r"^edit/$", views.edit.index, name="edit"),
        url(r"^edit/add$", views.edit.add_criterion, name="add-criterion"),
    ]


urlpatterns = sum([edit_patterns()], [])
