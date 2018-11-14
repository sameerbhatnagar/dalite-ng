import os

import pytest
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)


@pytest.yield_fixture
def browser(live_server):
    driver = webdriver.Firefox()
    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")


def test_fake_link(browser):
    email = "test@test.com"
    username, _ = get_student_username_and_password(email)
    token = create_student_token(username, email)

    signin_link = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(signin_link)

    err = (
        "There is no user corresponding to the given link. "
        "You may try asking for another one."
    )
    try:
        browser.find_element_by_xpath(
            "//*[contains(text(), '{}')]".format(err)
        )
    except NoSuchElementException:
        assert False


def test_new_student(browser):
    email = "test@test.com"

    browser.get("{}{}".format(browser.server_url, reverse("login")))

    try:
        login_link = browser.find_element_by_link_text("LOGIN")
    except NoSuchElementException:
        assert False
    login_link.click()

    try:
        input_ = browser.find_element_by_name("email")
    except NoSuchElementException:
        assert False

    input_.clear()
    input_.send_keys(email)
    input_.send_keys(Keys.ENTER)

    username, _ = get_student_username_and_password(email)
    token = create_student_token(username, email)

    signin_link = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(signin_link)

    try:
        browser.find_element_by_xpath(
            "//*[contains(text(), '{}')]".format(email)
        )
    except NoSuchElementException:
        assert False
