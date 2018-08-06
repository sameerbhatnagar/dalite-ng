from __future__ import unicode_literals
from operator import itemgetter

from django import forms
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


class EmailChangeForm(forms.Form):
    """Form for user email address"""
    email = forms.EmailField()


@login_required
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
        return HttpResponseBadRequest(resp.render())

    try:
        role_ = Role.objects.get(role=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'The role "{}" doesn\'t seem to exist.'.format(role)
                )
            },
        )

        return HttpResponseBadRequest(resp.render())

    email_types = [
        {
            "type": email_type.type,
            "title": email_type.title,
            "description": email_type.description,
            "accepted": EmailConsent.get(
                username, role, email_type.type, default=True, ignore_all=True
            ),
        }
        for email_type in EmailType.objects.filter(role=role_).order_by(
            "show_order"
        )
    ]

    # Handle e-mail address change form
    if req.method == "POST":
        form = EmailChangeForm(req.POST)
        if form.is_valid():
            req.user.email = form.cleaned_data["email"]
            req.user.save()
            redirect_to = req.GET.get("next", "/welcome/")
            return HttpResponseRedirect(redirect_to)
    else:
        form = EmailChangeForm()

    context = {
        "form": form,
        "username": username,
        "role": role,
        "email_types": email_types,
        "all_accepted": "all" not in list(map(itemgetter("type"), email_types))
        or next(e["accepted"] for e in email_types if e["type"] == "all"),
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
        return HttpResponseBadRequest(resp.render())

    try:
        role_ = Role.objects.get(role=role)
    except Role.DoesNotExist:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    'The role "{}" doesn\'t seem to exist.'.format(role)
                )
            },
        )

        return HttpResponseBadRequest(resp.render())

    consents = [
        {
            "user": req.user,
            "email_type": email_type,
            "accepted": req.POST.get(
                "{}-consent".format(email_type.type), False
            ),
        }
        for email_type in EmailType.objects.filter(role=role_)
    ]

    for consent in consents:
        EmailConsent.objects.create(**consent)

    redirect_to = req.POST.get("next", "/welcome/")

    return HttpResponseRedirect(redirect_to)
