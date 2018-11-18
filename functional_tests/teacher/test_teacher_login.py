from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys

from peerinst.students import (
    create_student_token,
    get_student_username_and_password,
)
from functional_tests.fixtures import *  # noqa F403


def test_teacher_login(browser, teacher):
    username = teacher.user.username
    password = "test"

    browser.get("{}{}".format(browser.server_url, reverse("login")))

    username_input = browser.find_element_by_xpath(
        "//input[@id=(//label[text()='Username']/@for)]"
    )
    username_input.clear()
    username_input.send_keys(username)

    password_input = browser.find_element_by_xpath(
        "//input[@id=(//label[text()='Password']/@for)]"
    )
    password_input.clear()
    password_input.send_keys(password)

    submit_button = browser.find_element_by_xpath("//input[@value='Submit']")
    submit_button.click()

    assert browser.current_url.endswith("browse/")
