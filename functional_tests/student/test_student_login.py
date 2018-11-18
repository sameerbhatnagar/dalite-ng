from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)
from functional_tests.fixtures import *  # noqa F403


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
    browser.find_element_by_xpath("//*[contains(text(), '{}')]".format(err))


def test_new_student(browser):
    email = "test@test.com"

    browser.get("{}{}".format(browser.server_url, reverse("login")))

    login_link = browser.find_element_by_link_text("LOGIN")
    login_link.click()

    input_ = browser.find_element_by_name("email")
    input_.clear()
    input_.send_keys(email)
    input_.send_keys(Keys.ENTER)

    username, _ = get_student_username_and_password(email)
    token = create_student_token(username, email)

    signin_link = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(signin_link)

    browser.find_element_by_xpath("//*[contains(text(), '{}')]".format(email))
