# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from dalite.views.errors import response_400

from ..logger import logger
from .teacher import teacher_reputation
from .utils import get_json_params


@login_required
def reputation(req):
    args = get_json_params(req, args=["reputation_type"])
    if isinstance(args, HttpResponse):
        return args
    (reputation_type,), __ = args

    if reputation_type == "teacher":
        return teacher_reputation(req)
    else:
        return response_400(
            req,
            msg=_("This isn't a supported reputation type."),
            logger_msg=(
                "The sent data used reputation type {} ".format(
                    reputation_type
                )
                + "which isn't supported."
            ),
            log=logger.warning,
        )
