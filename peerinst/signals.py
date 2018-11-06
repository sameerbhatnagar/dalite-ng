from django.core.signals import request_started
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

from .models import StudentNotificationType


@receiver(request_started)
def logger_signal(sender, environ, **kwargs):
    # message = request.path
    # user = str(request.user)
    # timestamp_request = str(timezone.now())
    # browser = request.META["HTTP_USER_AGENT"]
    # remote = request.META["REMOTE_ADDR"]
    # log = (
    #     user + " | " + timestamp_request + " | " + message + " | " +
    #     browser + " | " + remote
    # )
    if "HTTP_USER_AGENT" in environ:
        log = {}
        log["HTTP_REFERER"] = environ.get("HTTP_REFERER")
        log["HTTP_USER_AGENT"] = environ.get("HTTP_USER_AGENT")
        log["REMOTE_ADDR"] = environ.get("REMOTE_ADDR")
        log["QUERY_STRING"] = environ.get("QUERY_STRING")
        log["timestamp"] = str(timezone.now())
        # import pprint
        # pprint.pprint(log)
        pass


@receiver(post_migrate)
def student_notification_type_init_signal(sender, **kwargs):
    notifications = [
        {"type": "new_assignment", "icon": "assignment"},
        {"type": "assignment_about_to_expire", "icon": "assignment_late"},
        {"type": "assignment_due_date_changed", "icon": "schedule"},
    ]
    for notification in notifications:
        if not StudentNotificationType.objects.filter(
            type=notification["type"]
        ).exists():
            StudentNotificationType.objects.create(**notification)
