from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role, EmailType


@receiver(post_migrate)
def row_addition_signal(sender, **kwargs):
    roles = ("teacher", "student")

    for role in roles:
        Role.objects.create(role)
        EmailType.objects.create(**(all_email_type(role)))


def all_email_type(role):
    return {
        "role": role,
        "type": "all",
        "title": "All emails",
        "description": "Only receiver administrative emails from Dalite.",
    }
