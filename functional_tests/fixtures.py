import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from django.conf import settings

from peerinst.tests.fixtures import *  # noqa


@pytest.yield_fixture
def browser(live_server):
    if hasattr(settings, "HEADLESS_TESTING") and settings.HEADLESS_TESTING:
        os.environ["MOZ_HEADLESS"] = "1"
    try:
        driver = webdriver.Firefox()
    except WebDriverException:
        options = webdriver.ChromeOptions()
        if hasattr(settings, "HEADLESS_TESTING") and settings.HEADLESS_TESTING:
            options.add_argument("headless")
        driver = webdriver.Chrome(chrome_options=options)
    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")
