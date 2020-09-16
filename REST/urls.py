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
    r"disciplines", views.DisciplineViewSet, basename="discipline",
)
peerinst_api.register(
    r"assignment-questions",
    views.QuestionListViewSet,
    basename="assignment_question",
)
peerinst_api.register(
    r"questions", views.QuestionViewSet, basename="question",
)


urlpatterns = [
    path("peerinst/", include(peerinst_api.urls)),
    path(
        "search/questions/",
        views.QuestionSearchList.as_view(),
        name="question-search",
    ),
    path(
        "student/review/",
        views.StudentReviewList.as_view(),
        name="student-review",
    ),
    path(
        "student/feedback/",
        views.StudentFeedbackList.as_view(),
        name="student-feedback",
    ),
    path(
        "studentgroup/update/<int:pk>/",
        views.StudentGroupUpdateView.as_view(),
        name="student-group-update",
    ),
    path(
        "studentgroupassignment/",
        views.StudentGroupAssignmentAnswers.as_view({"get": "list"}),
        name="student-group-assigment-answers",
    ),
    path(
        "studentgroupassignment/<int:pk>/<int:question_pk>/",
        views.StudentGroupAssignmentAnswers.as_view({"get": "retrieve"}),
        name="student-group-assigment-answers",
    ),
    path("teacher/<int:pk>/", views.TeacherView.as_view(), name="teacher",),
    path(
        "teacher/search/",
        views.TeacherSearch.as_view({"get": "list"}),
        name="teacher-search",
    ),
    path(
        "teacher/feedback/",
        views.TeacherFeedbackList.as_view(),
        name="teacher-feedback-list",
    ),
    path(
        "teacher/feedback/<int:pk>/",
        views.TeacherFeedbackDetail.as_view(),
        name="teacher-feedback-detail",
    ),
    path(
        "teacher/feedback/through_answer/<int:pk>/",
        views.TeacherFeedbackThroughAnswerDetail.as_view(),
        name="teacher-feedback-through-answer-detail",
    ),
]
