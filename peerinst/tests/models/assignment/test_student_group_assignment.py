import random
from datetime import datetime, timedelta
from operator import itemgetter

import pytest
import pytz
from django.test import TestCase

from peerinst.models import StudentGroupAssignment
from peerinst.tests.generators import (
    add_answer_choices,
    add_answers,
    add_assignments,
    add_groups,
    add_questions,
    add_student_assignments,
    add_student_group_assignments,
    add_students,
    add_to_group,
    new_assignments,
    new_groups,
    new_questions,
    new_student_assignments,
    new_student_group_assignments,
    new_students,
)


@pytest.fixture
def student():
    return add_students(new_students(1))[0]


@pytest.fixture()
def group():
    return add_groups(new_groups(1))[0]


@pytest.fixture
def assignment():
    questions = add_questions(new_questions(10))
    return add_assignments(new_assignments(1, questions, min_questions=10))[0]


@pytest.fixture
def student_group_assignment():
    group = add_groups(new_groups(1))
    questions = add_questions(new_questions(10))
    assignment = add_assignments(
        new_assignments(1, questions, min_questions=10)
    )
    return add_student_group_assignments(
        new_student_group_assignments(1, group, assignment)
    )[0]


@pytest.mark.django_db
def test_new_student_group_assignment(group, assignment):
    data = new_student_group_assignments(1, group, assignment)[0]
    n_questions = assignment.questions.count()
    student_group_assignment = StudentGroupAssignment.objects.create(**data)
    assert isinstance(student_group_assignment, StudentGroupAssignment)
    assert student_group_assignment.group == data["group"]
    assert student_group_assignment.assignment == data["assignment"]
    assert student_group_assignment.order == ",".join(
        map(str, range(n_questions))
    )


@pytest.mark.django_db
def test_is_expired_expired(group, assignment):
    student_group_assignment = add_student_group_assignments(
        new_student_group_assignments(
            1, group, assignment, due_date=datetime.now(pytz.utc)
        )
    )[0]
    assert student_group_assignment.is_expired()


@pytest.mark.django_db
def test_is_expired_not_expired(group, assignment):
    student_group_assignment = add_student_group_assignments(
        new_student_group_assignments(
            1,
            group,
            assignment,
            due_date=datetime.now(pytz.utc) + timedelta(days=1),
        )
    )[0]
    assert not student_group_assignment.is_expired()


@pytest.mark.django_db
def test_hashing(student_group_assignment):
    assert student_group_assignment == StudentGroupAssignment.get(
        student_group_assignment.hash
    )


@pytest.mark.django_db
def test_modify_order(student_group_assignment):
    k = student_group_assignment.assignment.questions.count()
    for _ in range(3):
        new_order = ",".join(map(str, random.sample(range(k), k=k)))
        err = student_group_assignment.modify_order(new_order)
        assert err is None
        assert new_order == student_group_assignment.order


@pytest.mark.django_db
def test_modify_order_wrong_type(student_group_assignment):
    new_order = [1, 2, 3]
    with pytest.raises(AssertionError):
        student_group_assignment.modify_order(new_order)

    new_order = "abc"
    err = student_group_assignment.modify_order(new_order)
    assert err == "Given `order` isn't a comma separated list of integers."

    new_order = "a,b,c"
    err = student_group_assignment.modify_order(new_order)
    assert err == "Given `order` isn't a comma separated list of integers."


@pytest.mark.django_db
def test_questions(student_group_assignment):
    k = len(student_group_assignment.questions)
    new_order = ",".join(map(str, random.sample(range(k), k=k)))
    err = student_group_assignment.modify_order(new_order)
    assert err is None
    for i, j in enumerate(map(int, new_order.split(","))):
        assert (
            student_group_assignment.questions[i]
            == student_group_assignment.assignment.questions.all()[j]
        )

    assert new_order == student_group_assignment.order


@pytest.mark.django_db
def test_get_question_by_idx(student_group_assignment):
    questions = student_group_assignment.questions
    for i, question in enumerate(questions):
        assert question == student_group_assignment.get_question(idx=i)


@pytest.mark.django_db
def test_get_question_regular(student_group_assignment):
    questions = student_group_assignment.questions
    for i, question in enumerate(questions):
        if i != 0 and i != len(questions) - 1:
            assert (
                student_group_assignment.get_question(
                    current_question=question, after=True
                )
                == questions[i + 1]
            )
            assert (
                student_group_assignment.get_question(
                    current_question=question, after=False
                )
                == questions[i - 1]
            )


@pytest.mark.django_db
def test_get_question_edges(student_group_assignment):
    questions = student_group_assignment.questions
    assert (
        student_group_assignment.get_question(
            current_question=questions[0], after=False
        )
        is None
    )
    assert (
        student_group_assignment.get_question(
            current_question=questions[-1], after=True
        )
        is None
    )


@pytest.mark.django_db
def test_get_question_assert_raised(student_group_assignment):
    # To be revised with assertions in method
    #  with pytest.raises(AssertionError):
    #  student_group_assignment.get_question(
    #  0, student_group_assignment.questions[0]
    #  )
    pass


class TestGetStudentProgress(TestCase):
    def setUp(self):
        n_questions = 3
        self.students = add_students(new_students(20))
        groups = add_groups(new_groups(1))
        add_to_group(self.students, groups)
        self.questions = add_questions(new_questions(n_questions))
        add_answer_choices(2, self.questions)
        assignments = add_assignments(
            new_assignments(1, self.questions, min_questions=n_questions)
        )
        self.assignment = add_student_group_assignments(
            new_student_group_assignments(1, groups, assignments)
        )[0]
        add_student_assignments(
            new_student_assignments(
                len(self.students), [self.assignment], self.students
            )
        )

    def test_no_questions_done(self):
        progress = self.assignment.get_student_progress()

        self.assertEqual(
            0,
            len(
                set(map(itemgetter("question_title"), progress))
                - set((q.title for q in self.questions))
            ),
        )
        for question in progress:
            self.assertEqual(len(self.students), len(question["students"]))
            self.assertEqual(0, question["first"])
            self.assertEqual(0, question["first_correct"])
            self.assertEqual(0, question["second"])
            self.assertEqual(0, question["second_correct"])

    def test_some_first_answers_done(self):
        times_answered = {
            q.pk: random.randrange(1, len(self.students))
            for q in self.questions
        }
        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in self.questions
                for student in self.students[: times_answered[question.pk]]
            ]
        )

        progress = self.assignment.get_student_progress()

        self.assertEqual(
            0,
            len(
                set(map(itemgetter("question_title"), progress))
                - set((q.title for q in self.questions))
            ),
        )
        for question in progress:
            question_ = next(
                q
                for q in self.questions
                if q.title == question["question_title"]
            )
            self.assertEqual(len(self.students), len(question["students"]))
            self.assertEqual(times_answered[question_.pk], question["first"])
            self.assertEqual(
                times_answered[question_.pk], question["first_correct"]
            )
            self.assertEqual(0, question["second"])
            self.assertEqual(0, question["second_correct"])

    def test_all_first_answers_done(self):
        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in self.questions
                for student in self.students
            ]
        )

        progress = self.assignment.get_student_progress()

        self.assertEqual(
            0,
            len(
                set(map(itemgetter("question_title"), progress))
                - set((q.title for q in self.questions))
            ),
        )
        for question in progress:
            self.assertEqual(len(self.students), len(question["students"]))
            self.assertEqual(len(self.students), question["first"])
            self.assertEqual(len(self.students), question["first_correct"])
            self.assertEqual(0, question["second"])
            self.assertEqual(0, question["second_correct"])

    def test_some_second_answers_done(self):
        times_first_answered = {
            q.pk: random.randrange(2, len(self.students))
            for q in self.questions
        }
        times_second_answered = {
            q.pk: random.randrange(1, times_first_answered[q.pk])
            for q in self.questions
        }
        answers = add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in self.questions
                for student in self.students[
                    times_second_answered[question.pk] : times_first_answered[
                        question.pk
                    ]
                ]
            ]
        )
        answers += add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                    "second_answer_choice": 1,
                    "chosen_rationale": random.choice(
                        [a for a in answers if a.question == question]
                    ),
                }
                for question in self.questions
                for student in self.students[
                    : times_second_answered[question.pk]
                ]
            ]
        )

        progress = self.assignment.get_student_progress()

        self.assertEqual(
            0,
            len(
                set(map(itemgetter("question_title"), progress))
                - set((q.title for q in self.questions))
            ),
        )
        for question in progress:
            question_ = next(
                q
                for q in self.questions
                if q.title == question["question_title"]
            )
            self.assertEqual(len(self.students), len(question["students"]))
            self.assertEqual(
                times_first_answered[question_.pk], question["first"]
            )

            self.assertEqual(
                times_first_answered[question_.pk], question["first_correct"]
            )
            self.assertEqual(
                times_second_answered[question_.pk], question["second"]
            )
            self.assertEqual(
                times_second_answered[question_.pk], question["second_correct"]
            )

    def test_all_second_answers_done(self):

        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                    "second_answer_choice": 1,
                    "chosen_rationale": None,
                }
                for question in self.questions
                for student in self.students
            ]
        )

        progress = self.assignment.get_student_progress()

        self.assertEqual(
            0,
            len(
                set(map(itemgetter("question_title"), progress))
                - set((q.title for q in self.questions))
            ),
        )
        for question in progress:
            self.assertEqual(len(self.students), len(question["students"]))
            self.assertEqual(len(self.students), question["first"])
            self.assertEqual(len(self.students), question["first_correct"])
            self.assertEqual(len(self.students), question["second"])
            self.assertEqual(len(self.students), question["second_correct"])
