from faker import Faker
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from functional_tests.fixtures import *  # noqa
from .utils import login, logout

fake = Faker()


def go_to_forums(browser, forum):
    icon = browser.find_element_by_xpath("//i[contains(text(), 'menu')]")
    icon.click()

    try:
        forum_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Forums"))
        )
        time.sleep(1)
        forum_button.click()
    except NoSuchElementException:
        pass

    assert "Forums" in browser.find_element_by_tag_name("h1").text
    assert forum.title in browser.page_source


def create_post(browser):
    try:
        button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#forum-list .mdc-list-item")
            )
        )
    except NoSuchElementException:
        pass

    button.click()
    assert "Posts" in browser.find_element_by_tag_name("h2").text

    browser.find_element_by_link_text("Create a new post").click()
    assert "Create a New Post" in browser.find_element_by_tag_name("h1").text

    title = fake.sentence(nb_words=4)
    text = fake.paragraph()
    browser.find_element_by_id("id_title").send_keys(title)
    browser.find_element_by_id("id_content").send_keys(text)

    browser.find_element_by_css_selector("input[value='Create']").click()
    assert title in browser.find_element_by_tag_name("h2").text
    assert text in browser.page_source


def edit_post(browser):
    browser.find_element_by_link_text("Edit").click()

    title = fake.sentence(nb_words=4)
    input = browser.find_element_by_id("id_title")
    input.clear()
    input.send_keys(title)

    browser.find_element_by_css_selector("input[value='Update']").click()
    assert title in browser.find_element_by_tag_name("h2").text


def post_to_post(browser):
    text = fake.paragraph()
    browser.find_element_by_id("id_content").send_keys(text)
    browser.find_element_by_css_selector("input[value='Post']").click()
    assert text in browser.find_element_by_class_name("mdc-card").text


def edit_reply(browser):
    browser.find_element_by_link_text("mode_edit").click()
    assert "Edit Reply" in browser.find_element_by_tag_name("h1").text

    text = fake.paragraph()
    input = browser.find_element_by_id("id_content")
    input.clear()
    input.send_keys(text)

    browser.find_element_by_css_selector("input[value='Update']").click()
    assert text in browser.find_element_by_class_name("mdc-card").text


def reply_to_post(browser):
    browser.find_element_by_class_name("reply-btn").click()

    text = fake.paragraph()
    input = browser.find_element_by_css_selector(
        ".reply-form textarea"
    ).send_keys(text)
    browser.find_element_by_css_selector("input[value='Reply']").click()

    assert text in browser.find_element_by_class_name("reply-to-reply").text


def delete_reply(browser):
    browser.find_element_by_link_text("mode_edit").click()
    assert "Edit Reply" in browser.find_element_by_tag_name("h1").text

    browser.find_element_by_link_text("DELETE").click()
    assert "Confirm Delete?" in browser.find_element_by_tag_name("h1").text

    assert "The following replies will also be deleted" in browser.page_source

    assert len(browser.find_elements_by_class_name("mdc-card")) == 2

    browser.find_element_by_css_selector("input[value='Delete']").click()

    assert len(browser.find_elements_by_class_name("mdc-card")) == 0


def toggle_follow(browser):
    # Check round trip
    post_title = browser.find_element_by_tag_name("h2").text
    browser.find_element_by_link_text("Follows").click()

    assert "Follows" in browser.find_element_by_tag_name("h1").text
    assert (
        "Threads you are following"
        in browser.find_element_by_tag_name("h2").text
    )
    browser.find_element_by_class_name("thread-subscription").click()

    assert post_title in browser.find_element_by_tag_name("h2").text

    # Unfollow
    browser.find_element_by_class_name("follow").click()
    browser.find_element_by_link_text("Follows").click()

    assert len(browser.find_elements_by_class_name("thread-subscription")) == 0

    assert "You are not currently following any threads" in browser.page_source
    browser.execute_script("window.history.go(-1)")

    refollow(browser, post_title)


def refollow(browser, post_title=None):
    # Refollow
    browser.find_element_by_class_name("follow").click()
    browser.find_element_by_link_text("Follows").click()

    assert len(browser.find_elements_by_class_name("thread-subscription")) == 1

    browser.find_element_by_class_name("thread-subscription").click()
    if post_title:
        assert post_title in browser.find_element_by_tag_name("h2").text


def unfollow_from_subscription_list(browser):
    browser.find_element_by_link_text("Follows").click()
    browser.find_element_by_css_selector("input[value='clear']").click()

    assert "You are not currently following any threads" in browser.page_source
    browser.execute_script("window.history.go(-1)")
    browser.execute_script("window.history.go(-1)")

    assert (
        browser.find_element_by_class_name("follow").text == "favorite_border"
    )


def go_to_post(browser):
    try:
        button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#forum-list .mdc-list-item")
            )
        )
    except NoSuchElementException:
        pass

    button.click()

    try:
        button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".thread-link"))
        )
    except NoSuchElementException:
        pass

    button.click()


def check_notifications(browser, assert_):
    icon = browser.find_element_by_xpath("//i[contains(text(), 'menu')]")
    icon.click()

    try:
        forum_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Forums"))
        )
    except NoSuchElementException:
        pass

    browser.wait_for(
        lambda: assert_(
            "New!" in browser.find_element_by_id("#icon-with-text-demo").text
        )
    )


def test_forum_workflow(browser, assert_, teachers, forum):
    teacher = teachers[0]
    login(browser, teacher)
    go_to_forums(browser, forum)
    create_post(browser)
    edit_post(browser)
    post_to_post(browser)
    edit_reply(browser)
    reply_to_post(browser)
    delete_reply(browser)
    toggle_follow(browser)
    unfollow_from_subscription_list(browser)
    refollow(browser)
    logout(browser, assert_)

    other_teacher = teachers[1]
    login(browser, other_teacher)
    go_to_forums(browser, forum)
    go_to_post(browser)
    post_to_post(browser)
    logout(browser, assert_)

    login(browser, teacher)
    check_notifications(browser, assert_)
