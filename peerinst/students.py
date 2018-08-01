import hashlib
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings

from .utils import create_token, verify_token


def create_student_token(email, exp=timedelta(weeks=16)):
    assert isinstance(email, basestring), "Precondition failed for `email`"

    payload = {"email": email}
    output = create_token(payload, exp=exp)

    assert isinstance(output, basestring), "Postcondition failed"
    return output


def verify_student_token(token):
    assert isinstance(token, basestring), "Precondition failed for `token`"

    payload, err = verify_token(token)
    try:
        email = payload["email"]
    except KeyError:
        email = None
        err = "This wasn't a student token"

    output = (email, err)
    assert (
        isinstance(output, tuple)
        and len(output) == 2
        and (output[0] is None != output[1] is None)
        and (email is None or isinstance(email, basestring))
        and (err is None or isinstance(err, basestring))
    ), "Postcondition failed"
    return output


def authenticate_student(token):
    assert isinstance(token, basestring), "Precondition failed for `token`"

    resp = None

    email, err = verify_token(token)

    if err is not None:
        resp = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "This page isn't valid. You can try asking for a new "
                    "login link."
                )
            },
        )
        output = HttpResponseBadRequest(resp.render())

    else:

        username, password = get_student_username_and_password(email)

        user = authenticate(
            username=student_info["username"],
            password=student_info["password"],
        )

        if user is None:
            resp = TemplateResponse(
                req,
                "401.html",
                context={
                    "message": _("The account hasn't been verified yet.")
                },
            )
            output = HttpResponseUnauthorized(resp.render())
        else:
            output = user

    assert isinstance(output, HttpResponse) or isinstance(
        output, User
    ), "Postcondition failed"
    return output


def get_student_username_and_password(email, max_username_length=30):
    assert isinstance(email, basestring), "Precondition failed for `email`"

    key = settings.SECRET_KEY

    username = hashlib.md5(email.encode()).hexdigest()[:max_username_length]
    password = hashlib.md5(
        ("{}:{}".format(username, key)).encode()
    ).hexdigest()

    output = (username, password)

    assert (
        isinstance(output, tuple)
        and len(output) == 2
        and isinstance(output[0], basestring)
        and isinstance(output[1], basestring)
    ), "Postcondition failed"
    return output
