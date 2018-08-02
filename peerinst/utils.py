from datetime import datetime, timedelta

import pytz
import jwt
from django.conf import settings


def create_token(payload, exp=timedelta(weeks=16)):
    assert isinstance(payload, dict), "Precondition failed for `payload`"
    assert isinstance(exp, timedelta), "Precondition failed for `exp`"

    key = settings.SECRET_KEY

    payload_ = payload.copy()
    payload_.update(
        {
            "aud": "dalite",
            "iat": datetime.now(pytz.utc),
            "exp": datetime.now(pytz.utc) + exp,
        }
    )

    output = jwt.encode(payload_, key)

    assert isinstance(output, basestring), "Postcondition failed"
    return output


def verify_token(token):
    assert isinstance(token, basestring), "Precondition failed for `token`"

    key = settings.SECRET_KEY

    payload, err = None, None

    try:
        payload = jwt.decode(token, key, audience="dalite")
    except KeyError:
        err = "Token was incorrectly created."
    except jwt.exceptions.ExpiredSignatureError:
        err = "Token expired"
    except jwt.InvalidTokenError:
        err = "Invalid token"

    output = (payload, err)
    assert (
        isinstance(output, tuple)
        and len(output) == 2
        and ((output[0] is None) != (output[1] is None))
        and (output[0] is None or isinstance(output[0], dict))
        and (output[1] is None or isinstance(output[1], basestring))
    ), "Postcondition failed"
    return output
