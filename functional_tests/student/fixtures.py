import os
import pytest
from selenium import webdriver

from peerinst.tests.generators import (
    add_groups,
    add_students,
    new_groups,
    new_students,
)


@pytest.yield_fixture
def browser(live_server):
    driver = webdriver.Firefox()
    driver.server_url = live_server.url
    yield driver
    driver.close()
    if os.path.exists("geckodriver.log"):
        os.remove("geckodriver.log")


@pytest.fixture
def student():
    student = add_students(new_students(1))[0]
    student.student.is_active = True
    student.student.save()
    return student


@pytest.fixture
def group():
    return add_groups(new_groups(1))[0]
