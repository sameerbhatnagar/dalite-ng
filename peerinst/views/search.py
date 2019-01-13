# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from ..mixins import student_check
from ..models import Category, Teacher


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
@require_GET
def search_users(request):
    """Return list of usernames"""
    if request.is_ajax():
        users = (
            Teacher.objects.filter(
                user__username__icontains=request.GET.get("term")
            )
            .exclude(user=request.user)
            .values_list("user__username", "user__pk")
        )

        return JsonResponse(
            [{"label": str(u[0]), "value": u[1]} for u in users], safe=False
        )
    else:
        # Bad request
        return TemplateResponse(request, "400.html", status=400)


@login_required
@user_passes_test(student_check, login_url="/access_denied_and_logout/")
@require_GET
def search_categories(request):
    """Return list of categories"""
    if request.is_ajax():
        categories = Category.objects.filter(
            title__icontains=request.GET.get("term")
        ).values_list("title", "id")

        return JsonResponse(
            [{"label": str(c[0]), "value": c[1]} for c in categories],
            safe=False,
        )
    else:
        # Bad request
        return TemplateResponse(request, "400.html", status=400)
