from django.urls import path

from . import views

app_name = "quality"


def edit_patterns():
    return [
        path("edit/", views.edit.index, name="edit"),
        path("edit/add/", views.edit.add_criterion, name="add-criterion"),
        path(
            "edit/update/",
            views.edit.update_criterion,
            name="update-criterion",
        ),
        path(
            "edit/remove/",
            views.edit.remove_criterion,
            name="remove-criterion",
        ),
        path(
            "edit/remove/<int:pk>/",
            views.edit.remove_criterion,
            name="remove-criterion_",
        ),
    ]


def validation_patterns():
    return [
        path(
            "validate/", views.validation.validate_rationale, name="validate",
        )
    ]


def evaluation_patterns():
    return [
        path(
            "evaluate/", views.evaluation.evaluate_rationale, name="evaluate",
        )
    ]


urlpatterns = sum(
    [edit_patterns(), validation_patterns(), evaluation_patterns()], []
)
