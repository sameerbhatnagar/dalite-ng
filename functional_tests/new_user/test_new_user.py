import time

from functional_tests.fixtures import *  # noqa


def test_new_user_signup(browser, assert_):
    # Hit landing page
    browser.get(browser.server_url + "/#Features")
    browser.wait_for(
        assert_("Features" in browser.find_element_by_tag_name("h1").text)
    )
    assert (
        "Login" in browser.find_element_by_id("link-to-login-or-welcome").text
    )
    browser.find_element_by_link_text("Signup").click()

    # Sign up page rendered
    browser.wait_for(
        assert_("Sign Up" in browser.find_element_by_tag_name("h1").text)
    )

    # New user can sign up
    browser.wait_for(assert_(browser.find_element_by_tag_name("form")))
    form = browser.find_element_by_tag_name("form")
    assert form.get_attribute("method").lower() == "post"

    inputbox = browser.find_element_by_id("id_email")
    inputbox.send_keys("test@test.com")

    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys("test")

    inputbox = browser.find_element_by_id("id_url")
    inputbox.clear()
    inputbox.send_keys("http://www.mydalite.org")

    browser.find_element_by_id("submit-btn").click()

    # New user redirected post sign up
    browser.wait_for(
        assert_(
            "Processing Request" in browser.find_element_by_tag_name("h1").text
        )
    )

    # New user cannot sign in
    browser.get(browser.server_url + "/login")
    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys("test")

    inputbox = browser.find_element_by_id("id_password")
    inputbox.send_keys("jka+sldfa+soih")

    browser.find_element_by_id("submit-btn").click()

    browser.wait_for(
        assert_(
            "your account has not yet been activated" in browser.page_source
        )
    )

    time.sleep(1)


def test_new_user_signup_with_email_server_error(browser, assert_, settings):
    settings.EMAIL_BACKEND = ""

    browser.get(browser.server_url + "/signup")

    form = browser.find_element_by_tag_name("form")
    assert form.get_attribute("method") == "post"

    inputbox = browser.find_element_by_id("id_email")
    inputbox.send_keys("test@test.com")

    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys("test")

    inputbox = browser.find_element_by_id("id_url")
    inputbox.clear()
    inputbox.send_keys("http://www.mydalite.org")

    browser.find_element_by_id("submit-btn").click()

    browser.wait_for(
        assert_(
            "An error occurred while processing your request"
            in browser.page_source
        )
    )

    time.sleep(1)
