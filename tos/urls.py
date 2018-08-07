from __future__ import unicode_literals
from django.conf.urls import url
from . import views

app_name = "tos"
urlpatterns = [
    url(r"^required/$", views.tos.tos_required, name="tos_required"),
    url(
        r"^tos/(?P<role>\w{1,})/(?P<version>\d{1,})/update/$",
        views.tos.tos_consent_update,
        name="tos_update",
    ),
    url(
        r"^tos/(?P<role>[a-z]{1,})/(?P<version>\d{1,})/modify/$",
        views.tos.tos_consent_modify,
        name="tos_modify",
    ),
    url(
        r"^tos/(?P<role>[a-z]{1,})/modify/$",
        views.tos.tos_consent_modify,
        name="tos_modify",
    ),
    url(
        r"^tos/(?P<role>[a-z]{1,})/(?P<version>\d{1,})/$",
        views.tos.tos_consent,
        name="tos_consent",
    ),
    url(
        r"^tos/(?P<role>[a-z]{1,})/$",
        views.tos.tos_consent,
        name="tos_consent",
    ),
    url(
        r"^email/(?P<role>[a-z]{1,})/modify$",
        views.email.email_consent_modify,
        name="email_modify",
    ),
    url(
        r"^email/(?P<role>[a-z]{1,})/update$",
        views.email.email_consent_update,
        name="email_update",
    ),
    url(
        r"^email/(?P<role>[a-z]{1,})/change$",
        views.email.change_user_email,
        name="email_change",
    ),
]
