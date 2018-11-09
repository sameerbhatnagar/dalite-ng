import threading
from datetime import datetime, timedelta

from .models import StudentGroupAssignment


def start_scheduled_events():
    """
    Starts all events which happen on specific dates (such as assignment about
    to expire emails).
    """
    verify_assignment_due_dates()


def verify_assignment_due_dates():
    """
    Verifies each day if each assignment is about to expire and not done and
    adds a student notification for it and possibly sends an email.
    """
    for assignment in StudentGroupAssignment.objects.all():
        assignment.check_reminder_status()

    next_check = datetime.now() + timedelta(days=1)
    next_check.replace(hout=0, minute=0, second=0, microsecond=0)

    timer = threading.Timer(
        (next_check - datetime.now()).seconds, verify_assignment_due_dates
    )
    timer.start()
