from django.core.urlresolvers import reverse

from functional_tests.fixtures import *  # noqa
from .utils import go_to_account, login, logout


def test_change_password(browser, assert_, teacher):
    login(browser, teacher)
    go_to_account(browser)
    browser.find_element_by_id("identity-section").click()
    browser.find_element_by_id("edit-user-btn").click()

    # Check content
    assert (
        "Back to My Account"
        in browser.find_element_by_class_name("admin-link").text
    )
    assert "Password change" in browser.find_element_by_tag_name("h2").text

    # Check breadcrumbs
    browser.find_element_by_link_text("Back to My Account").click()
    assert "My Account" in browser.find_element_by_tag_name("h1").text

    browser.find_element_by_id("identity-section").click()
    browser.find_element_by_id("edit-user-btn").click()

    browser.find_element_by_id("id_old_password").send_keys("test")
    browser.find_element_by_id("id_new_password1").send_keys("retest&987")
    browser.find_element_by_id("id_new_password2").send_keys("retest&987")

    browser.find_element_by_css_selector("input[type='submit']").click()

    assert (
        "Password successfully changed"
        in browser.find_element_by_tag_name("body").text
    )

    browser.find_element_by_link_text("Back to My Account").click()
    assert "My Account" in browser.find_element_by_tag_name("h1").text

    logout(browser, assert_)

    browser.get("{}{}".format(browser.server_url, reverse("login")))
    username_input = browser.find_element_by_xpath(
        "//input[@id=(//label[text()='Username']/@for)]"
    )
    username_input.clear()
    username_input.send_keys(teacher.user.username)

    password_input = browser.find_element_by_xpath(
        "//input[@id=(//label[text()='Password']/@for)]"
    )
    password_input.clear()
    password_input.send_keys("retest&987")

    submit_button = browser.find_element_by_xpath("//input[@value='Submit']")
    submit_button.click()

    assert browser.current_url.endswith("browse/")
