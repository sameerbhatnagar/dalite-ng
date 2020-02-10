import base64
import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as translate

from dalite.views.utils import with_json_params

from .. import forms
from ..models import NewUserRequest, Teacher, UserType, UserUrl
from ..tasks import mail_admins_async, send_mail_async

logger = logging.getLogger("peerinst-views")


def sign_up(request):
    template = "registration/sign_up.html"
    html_email_template_name = "registration/sign_up_admin_email_html.html"
    context = {}

    if request.method == "POST":
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            # Set new users as inactive until verified by an administrator
            form.instance.is_active = False
            form.save()
            # Notify administrators
            if not settings.EMAIL_BACKEND.startswith(
                "django.core.mail.backends"
            ):
                return HttpResponse(status=503)

            # TODO Adapt to different types of user
            NewUserRequest.objects.create(
                user=form.instance, type=UserType.objects.get(type="teacher")
            )
            UserUrl.objects.create(
                user=form.instance, url=form.cleaned_data["url"]
            )

            email_context = dict(
                user=form.cleaned_data["username"],
                date=timezone.now(),
                email=form.cleaned_data["email"],
                url=form.cleaned_data["url"],
                site_name="myDALITE",
            )
            mail_admins_async(
                "New user request",
                "Dear administrator,"
                "\n\nA new user {} was created on {}.".format(
                    form.cleaned_data["username"], timezone.now()
                )
                + "\n\nEmail: {}".format(form.cleaned_data["email"])
                + "\nVerification url: {}".format(form.cleaned_data["url"])
                + "\n\nAccess your administrator account to activate this "
                "new user."
                "\n\n{}://{}{}".format(
                    request.scheme, request.get_host(), reverse("dashboard")
                )
                + "\n\nCheers,"
                "\nThe myDalite Team",
                fail_silently=True,
                html_message=loader.render_to_string(
                    html_email_template_name,
                    context=email_context,
                    request=request,
                ),
            )

            return TemplateResponse(request, "registration/sign_up_done.html")
        else:
            context["form"] = form
    else:
        context["form"] = forms.SignUpForm()

    return render(request, template, context)


def new_user_approval_page(req: HttpRequest) -> HttpResponse:
    new_users = [
        {
            "username": request.user.username,
            "date_joined": request.user.date_joined,
            "email": request.user.email,
            "url": request.user.url.url,
            "type": request.type.type,
        }
        for request in NewUserRequest.objects.order_by("-user__date_joined")
    ]
    context = {"new_users": new_users}
    return render(req, "admin/peerinst/new_user_approval.html", context)


@with_json_params(args=["username", "approve"])
def verify_user(
    req: HttpRequest, username: str, approve: bool
) -> HttpResponse:
    request = NewUserRequest.objects.get(user__username=username)

    if approve:
        if request.type.type == "teacher":
            Teacher.objects.create(user=request.user)
        else:
            raise NotImplementedError(
                "The verification for user type {request.type.type} hasn't "
                "been implemented"
            )
        request.user.is_active = True
        request.user.save()

        link = "{}://{}{}".format(
            req.scheme,
            req.get_host(),
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": base64.urlsafe_b64encode(
                        force_bytes(request.user.pk)
                    ),
                    "token": default_token_generator.make_token(request.user),
                },
            ),
        )

        # Notify user
        send_mail_async(
            translate("Please verify your myDalite account"),
            "Dear {},".format(request.user.username)
            + "\n\nYour account has been recently activated. Please visit "
            "the following link to verify your email address and "
            "to set your password:\n\n"
            + link
            + "\n\nCheers,\nThe myDalite Team",
            "noreply@myDALITE.org",
            [request.user.email],
            fail_silently=True,
            html_message=loader.render_to_string(
                "registration/verification_email.html",
                context={"username": request.user.username, "link": link},
                request=req,
            ),
        )
        request.delete()
        logger.info(f"New user {username} approved")

    else:
        request.user.delete()
        logger.info(f"New user {username} refused")

    return HttpResponse("")
