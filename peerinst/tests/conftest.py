from django.conf import settings


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker("django_db")


def pytest_configure(config):
    setattr(settings, "CELERY_ALWAYS_EAGER", True)
