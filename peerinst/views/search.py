# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from ..mixins import student_check
from ..models import Teacher


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
@require_GET
def search_users(request):
    """Return list of usernames"""
    if request.is_ajax():
        users = (
            Teacher.objects.filter(
                user__username__contains=request.GET.get("term")
            )
            .exclude(user=request.user)
            .values_list("user__username", "user__pk")
        )

        return JsonResponse(
            [{"label": str(u[0]), "value": u[1]} for u in users], safe=False
        )
    else:
        # Bad request
        response = TemplateResponse(request, "400.html")
        return HttpResponseBadRequest(response.render())
