import json
import datetime
import logging

from django.core.management.base import BaseCommand

from peerinst.models import Answer, ShownRationale, LtiEvent

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

        min_date = datetime.datetime(
            day=1, month=options["month"], year=options["year"]
        )
        max_date = datetime.datetime(
            day=28, month=options["month"], year=options["year"]
        )

        event_logs = LtiEvent.objects.filter(
            timestamp__gte=min_date, timestamp__lte=max_date
        ).values_list("event_log", flat=True)
        print(len(event_logs))
        print("start loading shown rationales")
        print(str(datetime.datetime.now()))
        for e in event_logs:
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
                            if created:
                                print(obj.shown_for_answer, obj.shown_answer)
                    except KeyError:
                        print("No Rationales")
                        print(e_json)

                except Answer.DoesNotExist:
                    print(
                        "Not found : ",
                        e_json["username"],
                        e_json["event"]["question_id"],
                        e_json["event"]["assignment_id"],
                    )

        print("completed loading shown rationales")
        print(str(datetime.datetime.now()))
