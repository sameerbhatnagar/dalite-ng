from functional_tests.fixtures import *  # noqa F403
from django.core.urlresolvers import reverse
from peerinst.students import create_student_token
from selenium.webdriver.common.keys import Keys


def test_group_creation_using_shared_link_and_enter(browser, student, group):
    token = create_student_token(
        student.student.username, student.student.email
    )
    url = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(url)

    link = browser.find_element_by_xpath("//*[contains(text(), 'Add groups')]")
    link.click()

    group_link = "{}{}".format(
        browser.server_url, reverse("signup-through-link", args=(group.hash,))
    )

    input_ = browser.find_element_by_name("new-group")
    input_.send_keys(group_link)
    input_.send_keys(Keys.ENTER)

    import time

    time.sleep(2)

    browser.find_element_by_xpath(
        "//div[@class='student-group--title']/h3[contains(text(), '{}')]".format(  # noqa
            group.title
        )
    )


def test_group_creation_using_shared_link_and_join_click(
    browser, student, group
):
    token = create_student_token(
        student.student.username, student.student.email
    )
    url = "{}{}?token={}".format(
        browser.server_url, reverse("student-page"), token
    )

    browser.get(url)

    link = browser.find_element_by_xpath("//*[contains(text(), 'Add groups')]")
    link.click()

    group_link = "{}{}".format(
        browser.server_url, reverse("signup-through-link", args=(group.hash,))
    )

    input_ = browser.find_element_by_name("new-group")
    input_.send_keys(group_link)
    join_button = browser.find_element_by_xpath(
        "//*[contains(text(), 'Join')]"
    )
    join_button.click()

    import time

    time.sleep(5)

    browser.find_element_by_xpath(
        "//div[@class='student-group--title']/h3[contains(text(), '{}')]".format(  # noqa
            group.title
        )
    )
