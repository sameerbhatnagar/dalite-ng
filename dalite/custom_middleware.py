from django.template.response import TemplateResponse


def resp_405_middleware(get_response):
    def middleware(req):
        resp = get_response(req)
        if resp.status_code == 405:
            message = "Allowed methods: {allow}".format(allow=resp["Allow"])
            return TemplateResponse(
                req, "405.html", status=405, context={"message": message}
            ).render()
        else:
            return resp

    return middleware


def resp_set_headers_middleware(get_response):
    """
    Sets all wanted security headers common to all responses.
    """

    def middleware(req):
        resp = get_response(req)

        iframe_allowed_from = ["*.moodle.ca", "*.moodle.com", "edx.com"]

        csp = {
            "default-src": ["'self'", "*.mydalite.org"],
            "script-src": [
                "'self'",
                "ajax.googleapis.com",
                "cdn.polyfill.io",
                "www.youtube.com",
                "s.yytimg.com",
                "'unsafe-inline'",
            ],
            "style-src": [
                "'self'",
                "fonts.googleapis.com",
                "unpkg.com",
                "'unsafe-inline'",
            ],
            "img-src": ["*", "data:"],
            "media-src": ["*", "data:"],
            "frame-src": ["*"],
            "font-src": [
                "fonts.googleapis.com",
                "fonts.gstatic.com",
                "unpkg.com",
            ],
        }

        resp["Content-Security-Policy"] = ";".join(
            "{} {}".format(key, " ".join(val)) for key, val in csp.items()
        )
        resp["X-Frame-Options"] = "allow-from {}".format(
            " ".join(iframe_allowed_from)
        )
        resp["Referrer-Policy"] = "same-origin"

        return resp

    return middleware
