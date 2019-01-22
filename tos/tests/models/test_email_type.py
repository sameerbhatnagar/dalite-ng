from tos.models import EmailType

from ..fixtures import role  # noqa
from ..generators import new_email_types


def test_new_email_type(role):
    data = new_email_types(3, role)

    for i, d in enumerate(data):
        email_type = EmailType.objects.create(**d)
        assert isinstance(email_type, EmailType)
        assert email_type.role.role == d["role"].role
        assert email_type.type == d["type"]
        assert email_type.title == d["title"]
        assert email_type.description == d["description"]
        assert email_type.show_order == i + 1
