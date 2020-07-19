from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from REST import views

app_name = "REST"

peerinst_api = DefaultRouter()
peerinst_api.register(
    r"assignments", views.AssignmentViewSet, basename="assignment"
)
peerinst_api.register(
    r"assignment-questions",
    views.QuestionListViewSet,
    basename="assignment_question",
)


urlpatterns = [
    path("peerinst/", include(peerinst_api.urls)),
    path(
        "review/answers/",
        views.ReviewAnswersListView.as_view(),
        name="answer",
    ),
    path(
        "feedback/answers/",
        views.FeedbackAnswersListView.as_view(),
        name="answer-feedback",
    ),
]
