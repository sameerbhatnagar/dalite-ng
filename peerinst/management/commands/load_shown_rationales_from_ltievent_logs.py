import json
import datetime
import logging

from django.core.management.base import BaseCommand

from peerinst.models import Answer, ShownRationale, LtiEvent

LOGGER = logging.getLogger("peerinst")


class Command(BaseCommand):
    help = "make ShownRationale objects from LtiEvents"

    def handle(self, *args, **options):

        event_logs = LtiEvent.objects.all().values_list("event_log", flat=True)
        LOGGER.info("start loading shown rationales")
        LOGGER.info(str(datetime.datetime.now()))
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
                        LOGGER.info(
                            "Multiple : ",
                            e_json["username"],
                            e_json["event"]["question_id"],
                            e_json["event"]["assignment_id"],
                        )

                    for r in e_json["event"]["rationales"]:
                        obj, created = ShownRationale.objects.get_or_create(
                            shown_answer=Answer.objects.get(pk=r["id"]),
                            shown_for_answer=shown_for_answer,
                        )
                        if created:
                            LOGGER.info(obj.shown_for_answer, obj.shown_answer)

                except Answer.DoesNotExist:
                    LOGGER.info(
                        "Not found : ",
                        e_json["username"],
                        e_json["event"]["question_id"],
                        e_json["event"]["assignment_id"],
                    )

        LOGGER.info("completed loading shown rationales")
        LOGGER.info(str(datetime.datetime.now()))
