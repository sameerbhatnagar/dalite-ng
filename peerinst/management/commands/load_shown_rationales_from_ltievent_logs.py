from __future__ import print_function

import datetime
import json
import logging
import time

from django.core.management.base import BaseCommand

from peerinst.models import Answer, LtiEvent, ShownRationale

LOGGER = logging.getLogger("peerinst")


class Command(BaseCommand):
    help = """
    make ShownRationale objects from LtiEvents.ime t
    Output should be directed to a log file
    Since this function takes a long time on production db,
    do one month at a time
    """

    def add_arguments(self, parser):
        parser.add_argument("--month", type=int)
        parser.add_argument("--year", type=int)

    def handle(self, *args, **options):
        start = time.time()

        min_date = datetime.datetime(
            day=1, month=options["month"], year=options["year"]
        )
        max_date = datetime.datetime(
            day=28, month=options["month"], year=options["year"]
        )

        event_logs = LtiEvent.objects.filter(
            timestamp__gte=min_date, timestamp__lte=max_date
        ).values_list("event_log", flat=True)
        print("Start loading shown rationales")
        for i, e in enumerate(event_logs.iterator()):
            e_json = json.loads(e)
            if e_json["event_type"] == "save_problem_success":

                try:
                    try:
                        shown_for_answer = Answer.objects.get(
                            user_token=e_json["username"],
                            question_id=e_json["event"]["question_id"],
                            assignment_id=e_json["event"]["assignment_id"],
                        )
                    except Answer.MultipleObjectsReturned:
                        print()
                        print(
                            "Multiple : ",
                            e_json["username"],
                            e_json["event"]["question_id"],
                            e_json["event"]["assignment_id"],
                        )
                    try:
                        for r in e_json["event"]["rationales"]:
                            obj, created = ShownRationale.objects.get_or_create(  # noqa
                                shown_answer=Answer.objects.get(pk=r["id"]),
                                shown_for_answer=shown_for_answer,
                            )
                    except KeyError:
                        print()
                        print("No Rationales")
                        print(e_json)

                except Answer.DoesNotExist:
                    print()
                    print(
                        "Not found : ",
                        e_json["username"],
                        e_json["event"]["question_id"],
                        e_json["event"]["assignment_id"],
                    )

        print("Completed loading shown rationales")
        print("Took {:.2f} seconds".format(time.time() - start))
