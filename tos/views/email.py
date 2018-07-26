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


from ..models import EmailConsent, EmailType, Role


@login_required
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

    try:
        role_ = Role.objects.get(role=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "500.html",
            context={
                "message": _(
                    'The role "{}" doesn\'t seem to exist.'.format(role)
                )
            },
        )

        return HttpResponseServerError(resp.render()), None

    email_types = EmailType.objects.filter(role=role_).order_by("show_order")

    context = {
        "username": username,
        "role": role,
        "email_types": email_types,
        "redirect_to": req.GET.get("next", "/welcome/"),
    }
    return render(req, "tos/email_modify.html", context)


@login_required
@require_http_methods(["POST"])
def email_consent_update(req, role):
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

    try:
        role_ = Role.objects.get(role=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "500.html",
            context={
                "message": _(
                    'The role "{}" doesn\'t seem to exist.'.format(role)
                )
            },
        )

        return HttpResponseServerError(resp.render()), None
