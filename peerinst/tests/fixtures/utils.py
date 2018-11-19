import pytest
from django.test.client import Client


@pytest.fixture
def client():
    return Client()
