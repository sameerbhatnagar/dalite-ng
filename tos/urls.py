from django.conf.urls import url
from . import views

app_name = "tos"
urlpatterns = [
    url(r"^required/$", views.tos.tos_required, name="tos_required"),
    url(
        r"(?P<role>\w{1,})/(?P<version>\d{1,})/update/$",
        views.tos.consent_update,
        name="update",
    ),
    url(
        r"(?P<role>\w{1,})/(?P<version>\d{1,})/modify/$",
        views.tos.consent_modify,
        name="modify",
    ),
    url(r"(?P<role>\w{1,})/modify/$", views.tos.consent_modify, name="modify"),
    url(
        r"(?P<role>\w{1,})/(?P<version>\d{1,})/$",
        views.tos.consent,
        name="consent",
    ),
    url(r"(?P<role>\w{1,})/$", views.tos.consent, name="consent"),
]
