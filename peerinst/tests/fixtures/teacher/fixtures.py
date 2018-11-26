import pytest
from .generators import add_teachers, new_teachers
from ..tos import consent_to_tos, tos_teacher  # noqa


@pytest.fixture
def teacher(tos_teacher):
    teacher = add_teachers(new_teachers(1))[0]
    teacher.user.is_active = True
    teacher.user.save()
    consent_to_tos(teacher, tos_teacher)
    return teacher
