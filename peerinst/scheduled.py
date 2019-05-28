# import threading
import logging
import operator
from celery import shared_task
from dalite.celery import try_async

from .models import Question, MetaFeature, MetaSearch

# from datetime import datetime, timedelta

# from .models import StudentGroupAssignment
logger = logging.getLogger("peerinst-models")


@try_async
@shared_task
def update_question_meta_search_difficulty():
    qs = Question.objects.all()
    difficulty_levels = qs[0].get_matrix().keys()
    for d in difficulty_levels:
        f, created = MetaFeature.objects.create(
            key="difficulty", value=d, type="S"
        )
        if created:
            logger.info("new difficulty level created : " + f)

    for q in qs:
        level = max(q.get_matrix(), key=operator.itemgetter(1))[0]
        f = MetaFeature.objects.get(level)
        s = MetaSearch.objects.create(meta_feature=f, content_object=q)
        q.add(s)
        q.save()

    return


def start_scheduled_events():
    """
    Starts all events which happen on specific dates (such as assignment about
    to expire emails).
    """
    verify_assignment_due_dates()


def stop_scheduled_events():
    pass


def verify_assignment_due_dates(check_every=1):
    """
    Verifies each day if each assignment is about to expire and not done and
    adds a student notification for it and possibly sends an email.

    Parameters
    ----------
    check_every : int or float
        Days or fraction of days after which to recheck the assignment due
        dates
    """
    #  for assignment in StudentGroupAssignment.objects.all():
    #  assignment.check_reminder_status()
    #
    #  next_check = datetime.now() + timedelta(days=check_every)
    #  if round(check_every) == check_every:
    #  next_check.replace(hour=0, minute=0, second=0, microsecond=0)
    #  else:
    #  next_check.replace(minute=0, second=0, microsecond=0)
    #
    #  timer = threading.Timer(
    #  (next_check - datetime.now()).seconds, verify_assignment_due_dates
    #  )
    #  timer.setDaemon(True)
    #  timer.start()
    pass
