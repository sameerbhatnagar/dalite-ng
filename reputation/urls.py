from django.urls import path

from . import views

app_name = "reputation"


def reputation_patterns():
    return [
        path("reputation/", views.reputation.reputation, name="reputation")
    ]


urlpatterns = sum([reputation_patterns()], [])
