from django.core.signals import request_started
from django.dispatch import receiver
from django.utils import timezone


@receiver(request_started)
def logger_signal(sender, environ, **kwargs):
    # message = request.path
    # user = str(request.user)
    # timestamp_request = str(timezone.now())
    # browser = request.META["HTTP_USER_AGENT"]
    # remote = request.META["REMOTE_ADDR"]
    # log = (
    #     user + " | " + timestamp_request + " | " + message + " | " +
    #     browser + " | " + remote
    # )
    if "HTTP_USER_AGENT" in environ:
        log = {}
        log["HTTP_REFERER"] = environ.get("HTTP_REFERER")
        log["HTTP_USER_AGENT"] = environ.get("HTTP_USER_AGENT")
        log["REMOTE_ADDR"] = environ.get("REMOTE_ADDR")
        log["QUERY_STRING"] = environ.get("QUERY_STRING")
        log["timestamp"] = str(timezone.now())
        # import pprint
        # pprint.pprint(log)
        pass
