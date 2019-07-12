# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.http import require_POST

from .decorators import teacher_required


@teacher_required
@require_POST
def get_report_result(req, teacher):
    """
    Returns the result of the previously asked for report. If the report isn't
    ready yet, will return a 102 response.

    Parameters
    ----------
    req : HttpRequest
        Request with:
            parameters:
                task_id: int
                    Id of the celery task responsible for the report generation
                    sent with the first request for a report
    teacher : Teacher
        Teacher instance returned by `teacher_required` (not used)

    Returns
    -------
    Either
        JsonResponse
            Response with json data
                {
                }
        HttpResponse
            Empty 102 response (Processing)
    """
    pass
