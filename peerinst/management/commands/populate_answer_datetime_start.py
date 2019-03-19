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

LOGGER = logging.getLogger("peerinst")


class Command(BaseCommand):
    help = """
    Populate Answer.datetime_start field from LtiEvents.
    """

    def handle(self, *args, **options):
        start = time.time()

        start_date = datetime.datetime(
            day=1, month=9, year=2018, tzinfo=pytz.utc
        )
        end_date = datetime.datetime(
            day=24, month=1, year=2019, tzinfo=pytz.utc
        )

        for day_of_logs in make_daterange(start_date, end_date):
            print(day_of_logs)
            populate_answer_start_time_from_ltievent_logs(day_of_logs)

        print("Completed populating datetime_start for Answer objects")
        print("Took {:.2f} seconds".format(time.time() - start))
