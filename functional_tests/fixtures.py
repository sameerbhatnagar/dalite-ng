import os
import pytest
import time

from django.conf import settings
from functools import partial
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement

from peerinst.tests.fixtures import *  # noqa


# Wait decorator
def wait(fn):
    MAX_WAIT = 30

    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


# wait_for expects a function
@pytest.fixture
def assert_():
    def fct(statement):
        def f():
            assert statement

        return f

    return fct


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

    # Add an implicit wait function to handle latency in page loads
    @wait
    def wait_for(fn):
        return fn()

    driver.wait_for = wait_for

    # Add assertion that web console logs are null after any get() or click()
    # Log function for get
    def add_log(fct, driver, *args, **kwargs):
        result = fct(*args, **kwargs)

        logs = driver.get_log("browser")

        if isinstance(result, WebElement):
            print("Logs checked after: " + fct.func.__name__)
        else:
            print("Logs checked after: " + fct.__name__)

        assert len(logs) == 0, logs

        return result

    # Log function for finders
    def click_with_log(finder, driver, *args, **kwargs):
        web_element = finder(*args, **kwargs)

        _click = getattr(web_element, "click")
        setattr(web_element, "click", partial(add_log, _click, driver))

        return web_element

    # Update get()
    _get = getattr(driver, "get")
    setattr(driver, "get", partial(add_log, _get, driver))

    # Update find_*() to add logging to click() of passed WebElement
    for method in dir(driver):
        if "find_element_" in method or method == "get":
            _method = getattr(driver, method)
            if callable(_method):
                setattr(driver, method, partial(add_log, _method, driver))

    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")
