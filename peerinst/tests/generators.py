from __future__ import unicode_literals

import random
import string
from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User

from peerinst.models import (
    Assignment,
    Question,
    Student,
    StudentAssignment,
    StudentGroup,
    StudentGroupAssignment,
    Teacher,
)
from tos.models import Consent as TosConsent


def new_assignments(n, questions):
    def generator():
        chars = string.ascii_letters + string.digits + "_-."
        gen = _extra_chars_gen()
        while True:
            yield {
                "identifier": "{}{}".format(
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(1, 50))
                    ),
                    next(gen),
                ),
                "title": "".join(
                    random.choice(chars) for _ in range(random.randint(1, 50))
                ),
                "questions": random.sample(
                    questions, k=random.randint(1, len(questions))
                ),
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_groups(n):
    def generator():
        chars = string.ascii_letters + string.digits + "_-."
        gen = _extra_chars_gen()
        while True:
            yield {
                "name": "{}{}".format(
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(1, 50))
                    ),
                    next(gen),
                ),
                "title": "".join(
                    random.choice(chars) for _ in range(random.randint(1, 50))
                ),
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_questions(n):
    def generator():
        chars = string.ascii_letters + string.digits + "_-."
        gen = _extra_chars_gen()
        while True:
            yield {
                "title": "{}{}".format(
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(1, 50))
                    ),
                    next(gen),
                ),
                "text": "".join(
                    random.choice(chars) for _ in range(random.randint(1, 100))
                ),
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_students(n):
    def generator():
        chars = string.ascii_lowercase + string.digits + "_-."
        gen = _extra_chars_gen()
        while True:
            yield {
                "email": "{}@{}.{}".format(
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(1, 32))
                    ),
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(1, 10))
                    ),
                    "".join(
                        random.choice(chars)
                        for _ in range(random.randint(2, 3))
                    ),
                )
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_student_assignments(n, groups, students):
    def generator():
        while True:
            yield {
                "student": random.choice(students),
                "group_assignment": random.choice(groups),
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def new_student_group_assignments(n, groups, assignments):
    def generator():
        while True:
            if random.random() > 0.5:
                datetime_ = datetime.now(pytz.utc) + timedelta(
                    days=random.randint(1, 60)
                )
            else:
                datetime_ = None
            yield {
                "group": random.choice(groups),
                "assignment": random.choice(assignments),
                "due_date": datetime_,
            }

    gen = generator()
    return [next(gen) for _ in range(n)]


def add_assignments(assignments):
    assignments_ = [
        Assignment.objects.create(
            **{k: v for k, v in a.items() if k != "questions"}
        )
        for a in assignments
    ]
    for assignment, a in zip(assignments_, assignments):
        assignment.questions.add(*a["questions"])
    return assignments_


def add_groups(groups):
    return [StudentGroup.objects.create(**g) for g in groups]


def add_questions(questions):
    return [Question.objects.create(**q) for q in questions]


def add_students(students):
    return [Student.create(**s) for s in students]


def add_student_assignments(student_assignments):
    return [StudentAssignment.objects.create(**s) for s in student_assignments]


def add_student_group_assignments(group_assignments):
    return [
        StudentGroupAssignment.objects.create(**g) for g in group_assignments
    ]


def _extra_chars_gen():
    letters = string.ascii_letters
    indices = [0]
    while True:
        yield "".join(letters[i] for i in indices)
        for i in range(len(indices)):
            if indices[i] < len(letters) - 1:
                indices[i] += 1
                break
            else:
                if i == len(indices) - 1:
                    indices = [0] * len(indices)
                    indices.append(0)
                    break
