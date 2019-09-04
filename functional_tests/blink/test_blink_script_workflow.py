import time

from django.urls import reverse

from functional_tests.fixtures import *  # noqa
from functional_tests.teacher.utils import login


def test_blink_script(browser, second_browser, assert_, teacher):
    blink_url = "{}{}".format(
        browser.server_url,
        reverse("blink-waiting", args=(teacher.user.username,)),
    )
    second_browser.get(blink_url)
    time.sleep(5)

    login(browser, teacher)
    time.sleep(5)
