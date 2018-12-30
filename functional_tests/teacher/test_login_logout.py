from django.core.urlresolvers import reverse

from functional_tests.fixtures import *  # noqa


def login(browser, teacher):
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


def access_logged_in_account_from_landing_page(browser, teacher):
    browser.get(browser.server_url)
    link = browser.find_element_by_link_text(
        "Welcome back {}".format(teacher.user.username)
    )
    link.click()
    assert browser.current_url.endswith("browse/")


def logout(browser):
    icon = browser.find_element_by_xpath("//i[contains(text(), 'menu')]")
    icon.click()

    link = browser.find_element_by_xpath("//a[contains(text(), 'Logout')]")
    link.click()

    assert browser.current_url == browser.server_url + "/en/"

    browser.find_element_by_link_text("Login")
    browser.find_element_by_link_text("Signup")


def test_teacher_login_logout(browser, teacher):
    login(browser, teacher)
    access_logged_in_account_from_landing_page(browser, teacher)
    logout(browser)
