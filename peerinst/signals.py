from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.core.signals import request_started
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

from .models import LastLogout, StudentNotificationType, Teacher
from pinax.forums.models import ThreadSubscription


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


@receiver(user_logged_in)
def prepare_session(sender, request, user, **kwargs):
    """ Post log in signal used to set up any special session variables, like
        notifications. """
    try:
        teacher = Teacher.objects.get(user=user)
        # Check for forum notifications
        request.session["forum_notifications"] = []
        follows = ThreadSubscription.objects.filter(user=user).order_by(
            "thread__last_reply"
        )
        for i in follows.all():
            print(i.thread.last_post.created)
        try:
            last_logout = LastLogout.objects.get(user=user)
        except ObjectDoesNotExist:
            if follows:
                request.session["forum_notifications"] = True
        else:
            if (
                follows.last().thread.last_post.created
                > last_logout.last_logout
            ):
                request.session["forum_notifications"] = list(
                    follows.filter(
                        thread__last_reply__created__gt=last_logout.last_logout
                    ).values_list("id", flat=True)
                )
    except ObjectDoesNotExist:
        pass


@receiver(user_logged_out)
def last_logout(sender, request, user, **kwargs):
    try:
        last_logout = LastLogout.objects.get(user=user)
        last_logout.save()
    except ObjectDoesNotExist:
        last_logout = LastLogout.objects.create(user=user)
