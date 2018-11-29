import os
import pytest
from selenium import webdriver
from django.conf import settings

from peerinst.tests.fixtures import *  # noqa


@pytest.yield_fixture
def browser(live_server):
    if hasattr(settings, "HEADLESS_TESTING") and settings.HEADLESS_TESTING:
        os.environ["MOZ_HEADLESS"] = "1"
    driver = webdriver.Firefox()
    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")
