import pytest

from peerinst.models import StudentNotificationType


@pytest.mark.django_db
def test_notifications_types_exist():
    types = (
        "new_assignment",
        "assignment_about_to_expire",
        "assignment_due_date_changed",
    )

    for type_ in types:
        assert StudentNotificationType.objects.filter(type=type_).exists()
