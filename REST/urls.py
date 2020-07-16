from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from REST import views

app_name = "REST"

peerinst_api = DefaultRouter()
peerinst_api.register(
    r"assignments", views.AssignmentViewSet, basename="assignment"
)

urlpatterns = [path("peerinst/", include(peerinst_api.urls))]
