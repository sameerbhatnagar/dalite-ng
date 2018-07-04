from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render

from .models import Consent, Tos


def consent(req, username, role, version=None):
    _consent, context = _consent_view(req, username, role, version)
    if isinstance(_consent, HttpResponse):
        return _consent

    if _consent is None:
        return render(req, "tos/consent.html", context)
    elif _consent:
        return JsonResponse({"consent": True})
    else:
        return JsonResponse({"consent": False})


def consent_modify(req, username, role, version):
    _consent, context = _consent_view(req, username, role, version)
    if isinstance(_consent, HttpResponse):
        return _consent
    return render(req, "tos/consent.html", context)


def consent_update(req, username, role, version):
    if req.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if role not in Tos.ROLES:
        return HttpResponseBadRequest("Not a valid role")
    try:
        accepted = req.POST["accepted"].lower() == "true"
    except KeyError:
        return HttpResponseBadRequest("Missing parameters")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseBadRequest("User doesn't exist")
    try:
        tos = Tos.objects.get(role=role[:2], version=version)
    except Tos.DoesNotExist:
        return HttpResponseBadRequest(
            "There is no terms of service with version "
            '{} for role "{}"'.format(version, role)
        )
    Consent.objects.create(user=user, tos=tos, accepted=accepted)
    if accepted:
        return HttpResponse("You've accepted!")
    return HttpResponse("You've refused...")


def _consent_view(req, username, role, version):
    if req.method != "GET":
        return HttpResponseNotAllowed(["GET"]), None
    if role not in Tos.ROLES:
        return HttpResponseBadRequest("Not a valid role"), None
    if not User.objects.filter(username=username).exists():
        return HttpResponseBadRequest("User doesn't exist"), None

    version = int(version) if version is not None else version

    if not Tos.objects.filter(role=role[:2]):
        return (
            HttpResponseServerError(
                "There isn't any terms of service version yet."
            ),
            None,
        )

    tos, err = Tos.get(role=role, version=version)

    if tos is None:
        return HttpResponseBadRequest(err), None

    _consent = Consent.get(username=username, role=role, version=version)

    context = {
        "username": username,
        "role": role,
        "tos_text": tos.text,
        "version": tos.version,
        "current": tos.current,
    }

    return _consent, context
