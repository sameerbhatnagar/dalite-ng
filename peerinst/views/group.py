# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from peerinst.models import StudentGroup, StudentGroupAssignment, Teacher


@login_required
@require_http_methods(["GET"])
def group_details_page(req, teacher_id, group_hash):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'There is no teacher with id "{}".'.format(teacher_id)
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    if req.user != teacher.user:
        resp = TemplateResponse(
            req,
            "403.html",
            context={"message": _("You do not have access to this page.")},
        )
        return HttpResponseForbidden(resp.render())

    group = StudentGroup.get(group_hash)
    if group is None:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'There is no group with hash "{}".'.format(group_hash)
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    assignments = StudentGroupAssignment.objects.filter(group=group)

    print(group.teacher.all())
    context = {"group": group, "assignments": assignments, "teacher": teacher}

    return render(req, "peerinst/group/details.html", context)
