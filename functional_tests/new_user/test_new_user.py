import time

from functional_tests.fixtures import *  # noqa
from tos.models import Role, Tos


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


def test_inactive_user_login(browser, assert_, inactive_user):

    # Inactive user cannot login
    browser.get(browser.server_url + "/login")
    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys(inactive_user.username)

    inputbox = browser.find_element_by_id("id_password")
    inputbox.send_keys("default_password")

    browser.find_element_by_id("submit-btn").click()

    browser.wait_for(
        assert_(
            "your account has not yet been activated" in browser.page_source
        )
    )

    time.sleep(1)


def test_new_teacher(browser, assert_, new_teacher, tos_teacher):

    # Teacher can login and access account
    browser.get(browser.server_url + "/login")
    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys(new_teacher.user.username)

    inputbox = browser.find_element_by_id("id_password")
    inputbox.send_keys("default_password")

    browser.find_element_by_id("submit-btn").click()

    # Redirected to Browse Database
    browser.wait_for(
        assert_(
            "Browse Database"
            in browser.find_elements_by_tag_name("h1")[0].text
        )
    )

    browser.find_element_by_xpath("//a[text()='Go to My Account']").click()

    # Access to account redirected to TOS if no TOS registered
    browser.wait_for(
        assert_(
            "Terms of Service"
            in browser.find_elements_by_tag_name("h1")[0].text
        )
    )

    browser.find_element_by_id("tos-accept").click()

    # Redirected to My Account and show TOS status
    browser.wait_for(
        assert_(
            "My Account" in browser.find_elements_by_tag_name("h1")[0].text
        )
    )
    assert "Terms of service: Sharing" in browser.page_source

    # Welcome authenticated user on landing page
    browser.get(browser.server_url)
    welcome = browser.find_element_by_id("link-to-login-or-welcome")
    browser.wait_for(
        assert_("Welcome back " + new_teacher.user.username in welcome.text)
    )

    # Logout and log back in -> skip tos step
    browser.get(browser.server_url + "/logout")
    browser.get(browser.server_url + "/login")

    inputbox = browser.find_element_by_id("id_username")
    inputbox.send_keys(new_teacher.user.username)

    inputbox = browser.find_element_by_id("id_password")
    inputbox.send_keys("default_password")

    browser.find_element_by_id("submit-btn").click()

    browser.find_element_by_xpath("//a[text()='Go to My Account']").click()

    browser.wait_for(
        assert_(
            "My Account" in browser.find_elements_by_tag_name("h1")[0].text
        )
    )

    # Add a new current TOS for teachers and refresh account -> back to tos
    role = Role.objects.get(role="teacher")
    new_TOS = Tos(version=2, text="Test 2", current=True, role=role)
    new_TOS.save()

    browser.get(browser.server_url + "/login")

    browser.find_element_by_xpath("//a[text()='Go to My Account']").click()

    browser.wait_for(
        assert_(
            "Terms of Service"
            in browser.find_elements_by_tag_name("h1")[0].text
        )
    )
    browser.find_element_by_id("tos-accept").click()

    # Teacher generally redirected to welcome page if logged in
    browser.get(browser.server_url + "/login")

    browser.wait_for(
        assert_(
            "Browse Database"
            in browser.find_elements_by_tag_name("h1")[0].text
        )
    )

    time.sleep(1)
