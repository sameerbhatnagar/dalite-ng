import hashlib
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.conf import settings

import jwt


def create_student_token(username, email, exp=timedelta(weeks=16)):
    assert isinstance(
        username, basestring
    ), "Precondition failed for `username`"
    assert isinstance(email, basestring), "Precondition failed for `email`"

    key = settings.SECRET_KEY

    payload = {
        "username": username,
        "email": email,
        "aud": "dalite",
        "iat": datetime.now(pytz.utc),
        "exp": datetime.now() + exp,
    }

    output = jwt.encode(payload, key)

    assert isinstance(output, basestring), "Postcondition failed"
    return output


def verify_token(token):
    assert isinstance(token, basestring), "Precondition failed for `token`"

    key = settings.SECRET_KEY

    username, email, err = None, None

    try:
        payload = jwt.decode(token, key)
        username = payload["username"]
        email = payload["email"]
    except KeyError:
        err = "Token was incorrectly created."
    except jwt.exceptions.ExpiredSignatureError:
        err = "Token expired"
    except jwt.InvalidTokenError:
        err = "Invalid token"

    output = (email, err)
    assert (
        isinstance(output, tuple)
        and len(output) == 2
        and (output[0] is None != output[1] is None)
        and (email is None or isinstance(email, basestring))
        and (err is None or isinstance(err, basestring))
    ), "Postcondition failed"
    return output


def login_student(token):
    assert isinstance(token, basestring), "Precondition failed for `token`"

    resp = None

    email, err = verify_token(token)

    if err is not None:
        template = TemplateResponse(
            req,
            "400.html",
            context={
                "message": _(
                    "This page isn't valid. You can try asking for a new "
                    "login link."
                )
            },
        )
        resp = HttpResponseBadRequest(template.render())

    else:

        username, password = get_student_username_and_password(email)

        user = authenticate(
            username=student_info["username"],
            password=student_info["password"],
        )

        if user is None:
            template = TemplateResponse(
                req,
                "401.html",
                context={
                    "message": _("The account hasn't been verified yet.")
                },
            )
            resp = HttpResponseUnauthorized(template.render())

    output = resp
    assert output is None or isinstance(
        output, HttpResponse
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
