from django.contrib.auth.signals import user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.signals import request_started
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import LastLogout, StudentNotificationType, TeacherNotification
from pinax.forums.models import ForumReply, ThreadSubscription


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


@receiver(post_save, sender=ForumReply)
def add_forum_notifications(sender, instance, created, **kwargs):
    notification_type = ContentType.objects.get(
        app_label="pinax_forums", model="ThreadSubscription"
    )
    print(instance)
    for s in ThreadSubscription.objects.filter(thread=instance.thread):
        print(s)
        try:
            notification = TeacherNotification.objects.create(
                teacher=s.user.teacher,
                notification_type=notification_type,
                object_id=s.id,
            )
            notification.save()
        except Exception:
            pass


@receiver(post_delete, sender=ThreadSubscription)
def delete_forum_notifications(sender, instance, **kwargs):
    notification_type = ContentType.objects.get(
        app_label="pinax_forums", model="ThreadSubscription"
    )
    try:
        notification = TeacherNotification.objects.get(
            notification_type=notification_type, object_id=instance.pk
        )
        notification.delete()
    except Exception:
        pass


@receiver(user_logged_out)
def last_logout(sender, request, user, **kwargs):
    try:
        last_logout = LastLogout.objects.get(user=user)
        last_logout.save()
    except ObjectDoesNotExist:
        last_logout = LastLogout.objects.create(user=user)
