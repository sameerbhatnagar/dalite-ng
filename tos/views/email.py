from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods


from ..models import EmailConsent


@require_http_methods(["GET"])
def email_consent_modify(req, role):
    username = req.user.username

    if not User.objects.filter(username=username).exists():
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _('The user "{}" doesn\'t exist.'.format(username))
            },
        )
        return HttpResponseBadRequest(resp.render()), None

    context = {
        "username": username,
        "role": role,
        "redirect_to": req.GET.get("next", "/welcome/"),
    }
