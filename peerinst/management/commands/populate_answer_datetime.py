from __future__ import print_function

import datetime
import logging
import time
import pytz

from django.core.management.base import BaseCommand

from peerinst.util import (
    populate_answer_start_time_from_ltievent_logs,
    make_daterange,
)

LOGGER = logging.getLogger("peerinst-models")


class Command(BaseCommand):
    help = """
    Populate Answer.datetime fields from LtiEvents.
    """

    def add_arguments(self, parser):
        parser.add_argument("event_type", nargs="+", type=str)

    def handle(self, *args, **options):
        start = time.time()

        start_date = datetime.datetime(
            day=2, month=9, year=2018, tzinfo=pytz.utc
        )
        end_date = datetime.datetime(
            day=1, month=10, year=2018, tzinfo=pytz.utc
        )

        event_type = options["event_type"][0]

        for day_of_logs in make_daterange(start_date, end_date):
            LOGGER.info(day_of_logs)
            populate_answer_start_time_from_ltievent_logs(
                day_of_logs=day_of_logs, event_type=event_type
            )

        LOGGER.info("Completed populating datetime_start for Answer objects")
        LOGGER.info("Took {:.2f} seconds".format(time.time() - start))
