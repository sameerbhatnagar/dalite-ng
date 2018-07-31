from datetime import datetime, timedelta
import pytz
import pyjwt
import settings


def create_token(username, exp=timedelta(weeks=16)):
    assert isinstance(
        username, basestring
    ), "Precondition failed for `username`"

    key = settings.SECRET_KEY

    payload = {
        "username": username,
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

    username, err = None, None

    try:
        username = jwt.decode(token, key)["username"]
    except KeyError:
        err = "Token was incorrectly created."
    except jwt.exceptions.ExpiredSignatureError:
        err = "Token expired"
    except jwt.InvalidTokenError:
        err = "Invalid token"

    output = (username, err)
    assert (
        isinstance(output, tuple)
        and (output[0] is None != output[1] is None)
        and (username is None or isinstance(username, basestring))
        and (err is None or isinstance(err, basestring))
    ), "Postcondition failed"
    return output
