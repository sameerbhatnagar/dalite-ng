from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from ..models import Consent, Tos, Role


@login_required
@require_http_methods(["GET"])
def tos_consent(req, role, version=None):
    username = req.user.username
    _consent, context = _consent_view(req, username, role, version)
    if isinstance(_consent, HttpResponse):
        return _consent

    if _consent is None:
        return render(req, "tos/tos_modify.html", context)
    elif _consent:
        return JsonResponse({"consent": True})
    else:
        return JsonResponse({"consent": False})


@login_required
@require_http_methods(["GET"])
def tos_consent_modify(req, role, version=None):
    username = req.user.username
    _consent, context = _consent_view(req, username, role, version)
    if isinstance(_consent, HttpResponse):
        return _consent
    return render(req, "tos/tos_modify.html", context)


@login_required
@require_http_methods(["POST"])
def tos_consent_update(req, role, version):
    try:
        r = Role.objects.get(role__iexact=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _('"{}" isn\'t a valid role.'.format(role))},
        )
        return HttpResponseBadRequest(resp.render())

    username = req.user.username

    try:
        accepted = req.POST["accepted"].lower() == "true"
    except KeyError:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _("There are missing parameters.")},
        )
        return HttpResponseBadRequest(resp.render())

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _('The user "{}" doesn\'t exist.'.format(username))
            },
        )
        return HttpResponseBadRequest(resp.render())

    try:
        tos = Tos.objects.get(role=r, version=version)
    except Tos.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "There is no terms of service with version "
                    '{} for role "{}"'.format(version, role)
                )
            },
        )
        return HttpResponseBadRequest(resp.render())

    Consent.objects.create(user=user, tos=tos, accepted=accepted)

    redirect_to = req.POST.get("redirect_to", "/welcome/")

    return HttpResponseRedirect(redirect_to)


def _consent_view(req, username, role, version):

    try:
        r = Role.objects.get(role__iexact=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={"message": _('"{}" isn\'t a valid role.'.format(role))},
        )
        return HttpResponseBadRequest(resp.render()), None
    if not User.objects.filter(username=username).exists():
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _('The user "{}" doesn\'t exist.'.format(username))
            },
        )
        return HttpResponseBadRequest(resp.render()), None

    version = int(version) if version is not None else version

    if not Tos.objects.filter(role=r):
        resp = TemplateResponse(
            req,
            "404.html",
            context={"message": _("There is no terms of service yet.")},
        )
        return HttpResponseNotFound(resp.render()), None

    tos, err = Tos.get(role=role, version=version)

    if tos is None:
        resp = TemplateResponse(req, "400.html", context={"message": _(err)})
        return HttpResponseBadRequest(resp.render()), None

    _consent = Consent.get(username=username, role=role, version=version)

    context = {
        "username": username,
        "role": role,
        "tos_text": tos.text,
        "version": tos.version,
        "current": tos.current,
        "redirect_to": req.GET.get("next", "/welcome/"),
    }

    return _consent, context


@login_required
def tos_required(req):
    resp = TemplateResponse(req, "tos/tos_required.html")
    return HttpResponseForbidden(resp.render())
