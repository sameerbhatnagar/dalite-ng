import pytest
from .generators import add_students, new_students
from ..tos import consent_to_tos, tos_student  # noqa


@pytest.fixture
def student(tos_student):
    student = add_students(new_students(1))[0]
    student.student.is_active = True
    student.student.save()
    consent_to_tos(student, tos_student)
    return student


@pytest.fixture
def students(tos_student):
    students = add_students(new_students(2))
    for student in students:
        student.student.is_active = True
        student.student.save()
        consent_to_tos(student, tos_student)
    return students


@pytest.fixture
def student_new(tos_student):
    student = add_students(new_students(1))[0]
    return student
