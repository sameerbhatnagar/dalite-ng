# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@login_required
@require_safe
def index(req):
    assignment_pk = req.GET.get("assignment")
    next_ = req.GET.get("next")

    context = {"data": {"next": next_}}

    return render(req, "quality/edit/index.html", context)
