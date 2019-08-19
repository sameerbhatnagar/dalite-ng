from django.core.urlresolvers import reverse

from functional_tests.fixtures import *  # noqa
from .utils import go_to_account, login, logout


def start(browser, teacher):
    login(browser, teacher)
    go_to_account(browser)
    browser.find_element_by_id("identity-section").click()


def test_change_password(browser, assert_, teacher):
    start(browser, teacher)
    browser.find_element_by_id("email-modify-btn").click()

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


def test_email_address_change(browser, assert_, teacher):
    new_email_address = "new_email_address@test.com"

    start(browser, teacher)
    browser.find_element_by_id("email-modify-btn").click()
    assert "Email Settings" in browser.find_element_by_tag_name("h1").text

    browser.find_element_by_id("id_email").send_keys(new_email_address)
    browser.find_element_by_id("submit-email-change-btn").click()
    assert "My Account" in browser.find_element_by_tag_name("h1").text

    browser.find_element_by_id("identity-section").click()
    browser.wait_for(
        lambda: assert_(
            new_email_address
            in browser.find_element_by_id("edit-user-btn").text
        )
    )


def test_email_notification_change(browser, assert_, teacher):
    start(browser, teacher)
    browser.find_element_by_id("email-modify-btn").click()
    assert "Email Settings" in browser.find_element_by_tag_name("h1").text

    assert not browser.find_element_by_id(
        "submit-notification-change-btn"
    ).is_enabled()

    browser.find_element_by_id("btn-toggle-all").click()
    browser.find_element_by_id("submit-notification-change-btn").click()
    assert "My Account" in browser.find_element_by_tag_name("h1").text

    # Send an email... outbox should be empty

    # Reset password... outbox should have 1 message
