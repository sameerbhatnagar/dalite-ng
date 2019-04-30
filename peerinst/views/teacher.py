# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_safe

from peerinst.models import Teacher

from .decorators import teacher_required


@teacher_required
@require_safe
def teacher_page(req, teacher):
    context = {}

    return render(req, "peerinst/teacher/page.html", context)
