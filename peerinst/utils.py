# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from datetime import datetime, timedelta

import jwt
import pytz
from django.conf import settings


def create_token(payload, exp=timedelta(weeks=16)):
    key = settings.SECRET_KEY

    payload_ = payload.copy()
    payload_.update(
        {
            "aud": "dalite",
            "iat": datetime.now(pytz.utc),
            "exp": datetime.now(pytz.utc) + exp,
        }
    )

    return base64.urlsafe_b64encode(
        jwt.encode(payload_, key, algorithm="HS256").encode()
    ).decode()


def verify_token(token):
    key = settings.SECRET_KEY

    payload, err = None, None

    try:
        payload = jwt.decode(
            base64.urlsafe_b64decode(token.encode()).decode(),
            key,
            audience="dalite",
            algorithms="HS256",
        )
    except KeyError:
        err = "Token was incorrectly created."
    except jwt.exceptions.ExpiredSignatureError:
        err = "Token expired"
    except jwt.InvalidTokenError:
        err = "Invalid token"

    return payload, err
