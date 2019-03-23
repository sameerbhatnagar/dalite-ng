# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


def edit_patterns():
    return [
        url(r"^edit/$", views.edit.index, name="edit"),
        url(r"^edit/add/$", views.edit.add_criterion, name="add-criterion"),
        url(
            r"^edit/update/$",
            views.edit.update_criterion,
            name="update-criterion",
        ),
        url(
            r"^edit/remove/$",
            views.edit.remove_criterion,
            name="remove-criterion",
        ),
    ]


def validation_patterns():
    return [
        url(
            r"^validate/$",
            views.validation.validate_rationale,
            name="validate",
        )
    ]


urlpatterns = sum([edit_patterns(), validation_patterns()], [])
