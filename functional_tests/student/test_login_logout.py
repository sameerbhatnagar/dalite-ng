import re

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys

from functional_tests.fixtures import *  # noqa
from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)


def signin(browser, student, new=False):
    email = student.student.email

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

    if new:
        assert re.search(
            r"/(\w{2})/tos/tos/student/\?next=/\1/student/",
            browser.current_url,
        )
    else:
        assert re.search(r"/en/student/\?token=", browser.current_url)


def access_logged_in_account_from_landing_page(browser, student):
    browser.get(browser.server_url)
    link = browser.find_element_by_link_text(
        "Welcome back {}".format(student.student.email)
    )
    link.click()
    assert re.search(r"student/", browser.current_url)


def logout(browser, assert_):
    icon = browser.find_element_by_xpath("//i[contains(text(), 'menu')]")
    icon.click()

    logout_button = browser.find_element_by_link_text("Logout")
    browser.wait_for(assert_(logout_button.is_enabled()))
    logout_button.click()

    assert browser.current_url == browser.server_url + "/en/"

    browser.find_element_by_link_text("Login")
    browser.find_element_by_link_text("Signup")


def consent_to_tos(browser):
    share = browser.find_element_by_xpath(
        "//button[contains(text(), 'Share')]"
    )
    share.click()

    sharing = browser.find_element_by_id("student-tos-sharing--sharing")
    assert sharing.text == "Sharing"


def test_fake_link(browser):
    email = "test@test.com"
    username, _ = get_student_username_and_password(email)
    token = create_student_token(username, email)

    signin_link = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(signin_link)

    assert re.search(r"student/", browser.current_url)

    err = (
        "There is no user corresponding to the given link. "
        "You may try asking for another one."
    )
    browser.find_element_by_xpath("//*[contains(text(), '{}')]".format(err))


def test_student_login_logout(browser, assert_, student):
    signin(browser, student, new=False)
    access_logged_in_account_from_landing_page(browser, student)
    logout(browser, assert_)


def test_new_student_login(browser, student_new):
    signin(browser, student_new, new=True)
    consent_to_tos(browser)
