# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_safe

from dalite.views.errors import response_403

from .student import student_page
from .teacher import teacher_page

logger = logging.getLogger("peerinst-views")


@login_required
@require_safe
def page(req):
    if req.user.teacher:
        return teacher_page(req)
    elif req.user.student:
        return student_page(req)
    else:
        return response_403(
            req,
            msg=_("You don't have access to this resource."),
            logger_msg=(
                "Access to {} without a group or assignment hash.".format(
                    req.path
                )
            ),
            log=logger.warning,
        )
