from django.urls import re_path

from . import views

app_name = "quality"


def edit_patterns():
    return [
        re_path(r"^edit/$", views.edit.index, name="edit"),
        re_path(
            r"^edit/add/$", views.edit.add_criterion, name="add-criterion"
        ),
        re_path(
            r"^edit/update/$",
            views.edit.update_criterion,
            name="update-criterion",
        ),
        re_path(
            r"^edit/remove/$",
            views.edit.remove_criterion,
            name="remove-criterion",
        ),
        re_path(
            r"^edit/remove/<int:pk>/$",
            views.edit.remove_criterion,
            name="remove-criterion_",
        ),
    ]


def validation_patterns():
    return [
        re_path(
            r"^validate/$",
            views.validation.validate_rationale,
            name="validate",
        )
    ]


def evaluation_patterns():
    return [
        re_path(
            r"^evaluate/$",
            views.evaluation.evaluate_rationale,
            name="evaluate",
        )
    ]


urlpatterns = sum(
    [edit_patterns(), validation_patterns(), evaluation_patterns()], []
)
