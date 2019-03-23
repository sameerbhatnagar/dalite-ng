# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from dalite.views.errors import response_400

from ..models import Quality, RejectedAnswer

logger = logging.getLogger("quality")


@login_required
@require_POST
def validate_rationale(req):
    try:
        data = json.loads(req.body)
    except ValueError:
        return response_400(
            req,
            msg=_("Wrong data type was sent."),
            logger_msg=("The sent data wasn't in a valid JSON format."),
            log=logger.warning,
        )
    try:
        rationale = data["rationale"]
        quality_pk = data.get("quality")
    except KeyError as e:
        return response_400(
            req,
            msg=_("There are missing parameters."),
            logger_msg=(
                "The arguments {} were missing.".format(", ".join(e.args))
            ),
            log=logger.warning,
        )

    if quality_pk is None:
        quality = Quality.objects.get(quality_type__type="global")
    else:
        try:
            quality = Quality.objects.get(pk=quality_pk)
        except Quality.DoesNotExist:
            return response_400(
                req,
                msg=_("Some of the parameters were wrong."),
                logger_msg=(
                    "There isn't any quality with key {}.".format(quality_pk)
                ),
                log=logger.warning,
            )

    quality_, evaluation = quality.evaluate(rationale)

    if quality_ is not None and quality_ < quality.threshold:
        data = {
            "failed": [
                {"name": c["full_name"], "description": c["description"]}
                for c in evaluation
                if c["quality"]["quality"] < c["quality"]["threshold"]
            ]
        }
        RejectedAnswer.add(quality, rationale, evaluation)
    else:
        data = {}

    return JsonResponse(data)
