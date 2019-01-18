import os

import pytest
from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from peerinst.tests.fixtures import *  # noqa


@pytest.yield_fixture
def browser(live_server):
    if hasattr(settings, "TESTING_BROWSER"):
        browser = settings.TESTING_BROWSER.lower()
    else:
        browser = "firefox"

    if hasattr(settings, "HEADLESS_TESTING") and settings.HEADLESS_TESTING:
        os.environ["MOZ_HEADLESS"] = "1"
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
    else:
        options = webdriver.ChromeOptions()

    if browser == "firefox":
        try:
            driver = webdriver.Firefox()
        except WebDriverException:
            driver = webdriver.Chrome(options=options)
    elif browser == "chrome":
        try:
            driver = webdriver.Chrome(options=options)
        except WebDriverException:
            driver = webdriver.Firefox()
    else:
        raise ValueError(
            "The TESTING_BROWSER setting in local_settings.py must either be "
            "firefox or chrome."
        )

    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")
