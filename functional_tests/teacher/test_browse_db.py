import time

from selenium.webdriver.common.keys import Keys

from functional_tests.fixtures import *  # noqa
from .utils import login


def search(browser, assert_, realistic_questions):
    assert "Browse Database" in browser.find_element_by_tag_name("h1").text
    inputbox = browser.find_element_by_id("search-bar")
    inputbox.send_keys(realistic_questions[0].title)
    inputbox.send_keys(Keys.ENTER)

    # Assert question in results

    # Check filters

    # Check clear

    # Check answer toggle

    # Check re-search

    # Check only valid questions are searchable?

    time.sleep(2)


def test_search_function(browser, assert_, teacher, realistic_questions):
    login(browser, teacher)
    search(browser, assert_, realistic_questions)
