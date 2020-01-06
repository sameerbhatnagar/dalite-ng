# -*- coding: utf-8 -*-


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
        url(
            r"^edit/remove/<int:pk>/$",
            views.edit.remove_criterion,
            name="remove-criterion_",
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


def evaluation_patterns():
    return [
        url(
            r"^evaluate/$",
            views.evaluation.evaluate_rationale,
            name="evaluate",
        )
    ]


urlpatterns = sum(
    [edit_patterns(), validation_patterns(), evaluation_patterns()], []
)
