# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _

from dalite.views.errors import response_400
from peerinst.models import Teacher

from .decorators import logged_in_non_student_required
from .utils import get_json_params

logger = logging.getLogger("reputation")


@logged_in_non_student_required
def teacher_reputation(req):
    args = get_json_params(req, args=["teacher_id"])
    if isinstance(args, HttpResponse):
        return args
    (teacher_id,), __ = args

    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except (Teacher.DoesNotExist, AttributeError):
        return response_400(
            req,
            msg=_("This teacher doesn't exist."),
            logger_msg=(
                "Tried to obtain teacher with pk {}".format(teacher_id)
            ),
            log=logger.warning,
        )
