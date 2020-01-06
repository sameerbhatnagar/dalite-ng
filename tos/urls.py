from django.urls import re_path
from . import views

app_name = "tos"
urlpatterns = [
    re_path(r"^required/$", views.tos.tos_required, name="tos_required"),
    re_path(
        r"^tos/<role>/<int:version>/update/$",
        views.tos.tos_consent_update,
        name="tos_update",
    ),
    re_path(
        r"^tos/<role>/<int:version>/modify/$",
        views.tos.tos_consent_modify,
        name="tos_modify",
    ),
    re_path(
        r"^tos/<role>/modify/$",
        views.tos.tos_consent_modify,
        name="tos_modify",
    ),
    re_path(
        r"^tos/<role>/(?P<version>\d{1,})/$",
        views.tos.tos_consent,
        name="tos_consent",
    ),
    re_path(r"^tos/<role>/$", views.tos.tos_consent, name="tos_consent",),
    re_path(
        r"^email/<role>/modify$",
        views.email.email_consent_modify,
        name="email_modify",
    ),
    re_path(
        r"^email/<role>/update$",
        views.email.email_consent_update,
        name="email_update",
    ),
    re_path(
        r"^email/<role>/change$",
        views.email.change_user_email,
        name="email_change",
    ),
]
