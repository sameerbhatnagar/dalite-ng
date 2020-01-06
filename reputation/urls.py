from django.urls import re_path

from . import views

app_name = "reputation"


def reputation_patterns():
    return [
        re_path(
            r"^reputation/$", views.reputation.reputation, name="reputation"
        )
    ]


urlpatterns = sum([reputation_patterns()], [])
