import time

from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from functional_tests.fixtures import *  # noqa
from functional_tests.teacher.utils import accept_cookies, go_to_account, login


TIME = 30


def make_blink_script(_browser, q):
    _browser.find_element_by_id("blink-section").click()
    _browser.find_element_by_link_text("Add script").click()

    script_name = "New blink script"

    input = _browser.find_element_by_id("id_title")
    input.send_keys(script_name)
    input.send_keys(Keys.ENTER)

    assert "Update Script" in _browser.find_element_by_tag_name("h1").text
    assert script_name in _browser.find_element_by_tag_name("h2").text

    checkbox = _browser.find_element_by_id("limit-search")
    checkbox.click()

    search = _browser.find_element_by_id("search-bar")
    search.send_keys(q[0].title)
    search.send_keys(Keys.ENTER)

    time.sleep(1)
    assert q[0].title in _browser.find_element_by_id("search_results").text

    card = _browser.find_element_by_id("add-{}".format(q[0].pk)).click()

    search = _browser.find_element_by_id("search-bar")
    search.send_keys(q[1].title)
    search.send_keys(Keys.ENTER)

    time.sleep(1)
    assert q[1].title in _browser.find_element_by_id("search_results").text

    card = _browser.find_element_by_id("add-{}".format(q[1].pk)).click()

    go_to_account(_browser)


def start_blink_script(_browser):
    link = _browser.find_element_by_class_name("blink")
    link.click()

    input = _browser.find_element_by_id("id_time_limit")
    input.clear()
    input.send_keys(TIME)

    start_btn = _browser.find_element_by_xpath("//input[@value='Start']")
    start_btn.click()


def validate_teacher_page(_browser, q):
    time.sleep(2)
    assert "Blink Question" in _browser.find_element_by_tag_name("h1").text
    assert q.title in _browser.find_element_by_tag_name("h2").text


def validate_student_page(_browser, q):
    time.sleep(2)
    assert "Blink Question" in _browser.find_element_by_tag_name("h1").text
    assert q.title in _browser.find_element_by_tag_name("h2").text
    assert len(_browser.find_elements_by_class_name("mdc-radio")) > 0


def answer_blink(_browser, q, choice):
    _browser.find_elements_by_class_name("mdc-radio")[choice].click()
    _browser.find_element_by_id("submit-answer").click()

    assert "Blink Question" in _browser.find_element_by_tag_name("h1").text
    assert q.title in _browser.find_element_by_tag_name("h2").text


def test_blink_script(
    browser,
    second_browser,
    third_browser,
    assert_,
    realistic_questions,
    teacher,
):
    browser.set_window_rect(0, 0, 800, 1000)
    second_browser.set_window_rect(800, 0, 500, 1000)
    third_browser.set_window_rect(1300, 0, 500, 1000)

    blink_url = "{}{}".format(
        browser.server_url,
        reverse("blink-waiting", args=(teacher.user.username,)),
    )
    second_browser.get(blink_url)
    accept_cookies(second_browser)
    assert (
        "Waiting for teacher"
        in second_browser.find_element_by_tag_name("h2").text
    )

    third_browser.get(blink_url)
    accept_cookies(third_browser)
    assert (
        "Waiting for teacher"
        in third_browser.find_element_by_tag_name("h2").text
    )

    login(browser, teacher)
    accept_cookies(browser)
    go_to_account(browser)
    make_blink_script(browser, realistic_questions[:2])
    start_blink_script(browser)

    validate_teacher_page(browser, realistic_questions[0])
    validate_student_page(second_browser, realistic_questions[0])
    validate_student_page(third_browser, realistic_questions[0])

    assert browser.find_element_by_id("round").text == "1"

    print("Student one answers")
    answer_blink(second_browser, realistic_questions[0], 0)

    time.sleep(1)
    assert browser.find_element_by_id("counter").text == "1"

    print("Student two answers")
    answer_blink(third_browser, realistic_questions[0], 0)

    time.sleep(1)
    assert browser.find_element_by_id("counter").text == "2"

    try:
        reset_btn = WebDriverWait(browser, TIME).until(
            EC.element_to_be_clickable((By.ID, "reset_button"))
        )
        time.sleep(1)
        reset_btn.click()
    except NoSuchElementException:
        pass

    validate_teacher_page(browser, realistic_questions[0])
    validate_student_page(second_browser, realistic_questions[0])
    validate_student_page(third_browser, realistic_questions[0])

    print("Student one answers")
    answer_blink(second_browser, realistic_questions[0], 1)

    time.sleep(1)
    assert browser.find_element_by_id("round").text == "2"
    assert browser.find_element_by_id("counter").text == "1"

    print("Student two answers")
    answer_blink(third_browser, realistic_questions[0], 1)

    time.sleep(1)
    assert browser.find_element_by_id("round").text == "2"
    assert browser.find_element_by_id("counter").text == "2"

    try:
        next_btn = WebDriverWait(browser, TIME).until(
            EC.element_to_be_clickable((By.ID, "next_button"))
        )
        time.sleep(1)
        next_btn.click()
    except NoSuchElementException:
        pass

    validate_teacher_page(browser, realistic_questions[1])
    validate_student_page(second_browser, realistic_questions[1])
    validate_student_page(third_browser, realistic_questions[1])

    print("Student one answers")
    answer_blink(second_browser, realistic_questions[1], 2)

    time.sleep(1)
    assert browser.find_element_by_id("round").text == "1"
    assert browser.find_element_by_id("counter").text == "1"

    print("Student two answers")
    answer_blink(third_browser, realistic_questions[1], 2)

    time.sleep(1)
    assert browser.find_element_by_id("round").text == "1"
    assert browser.find_element_by_id("counter").text == "2"

    try:
        next_btn = WebDriverWait(browser, TIME).until(
            EC.element_to_be_clickable((By.ID, "next_button"))
        )
        time.sleep(1)
        next_btn.click()
    except NoSuchElementException:
        pass

    time.sleep(2)
    assert "My Account" in browser.find_element_by_tag_name("h1").text
    assert (
        "Waiting for teacher"
        in second_browser.find_element_by_tag_name("h2").text
    )
    assert (
        "Waiting for teacher"
        in third_browser.find_element_by_tag_name("h2").text
    )
