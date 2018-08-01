# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.test import TestCase
import hashlib
import pytz
from operator import add
from functools import reduce

from . import factories
from ..models import GradingScheme, StudentGroupAssignment
from .generators import *


class SelectedChoice(object):
    CORRECT = 1
    INCORRECT = 2


class AnswerModelTestCase(TestCase):
    def setUp(self):
        super(AnswerModelTestCase, self).setUp()
        # Create question with two choices (correct/incorrect):
        self.question = factories.QuestionFactory(
            choices=2, choices__correct=[1]
        )
        # Create answers for question, considering all possible combinations of correctness values:
        self.answers = []
        selected_choices = (
            (SelectedChoice.CORRECT, SelectedChoice.CORRECT),
            (SelectedChoice.CORRECT, SelectedChoice.INCORRECT),
            (SelectedChoice.INCORRECT, SelectedChoice.CORRECT),
            (SelectedChoice.INCORRECT, SelectedChoice.INCORRECT),
        )
        for first_answer_choice, second_answer_choice in selected_choices:
            answer = factories.AnswerFactory(
                question=self.question,
                first_answer_choice=first_answer_choice,
                second_answer_choice=second_answer_choice,
            )
            self.answers.append(answer)

    def _assert_grades(self, expected_grades):
        """ For each answer in `self.answers`, check if `get_grade` produces correct value. """
        for index, answer in enumerate(self.answers):
            grade = answer.get_grade()
            self.assertEqual(grade, expected_grades[index])

    def test_get_grade_standard(self):
        """
        Check if `get_grade` produces correct values when using 'Standard' grading scheme.

        | First choice | Second choice | Grade |
        |--------------+---------------+-------|
        | correct      | correct       | 1.0   |
        | correct      | incorrect     | 0.0   |
        | incorrect    | correct       | 1.0   |
        | incorrect    | incorrect     | 0.0   |
        """
        self._assert_grades(expected_grades=[1.0, 0.0, 1.0, 0.0])

    def test_get_grade_advanced(self):
        """
        Check if `get_grade` produces correct values when using 'Advanced' grading scheme.

        | First choice | Second choice | Grade |
        |--------------+---------------+-------|
        | correct      | correct       | 1.0   |
        | correct      | incorrect     | 0.5   |
        | incorrect    | correct       | 0.5   |
        | incorrect    | incorrect     | 0.0   |
        """
        self.question.grading_scheme = GradingScheme.ADVANCED
        self._assert_grades(expected_grades=[1.0, 0.5, 0.5, 0.0])


class TestStudent(TestCase):
    def test_new_student(self):
        n = 2
        max_username_length = 30
        data = new_students(n)

        for d in data:
            student = Student.create(**d)
            username = hashlib.md5(d["email"].encode()).hexdigest()[
                :max_username_length
            ]
            self.assertIsInstance(student, Student)
            self.assertEqual(student.student.email, d["email"])
            self.assertEqual(student.student.username, username)


class TestStudentGroup(TestCase):
    def test_new_student_group(self):
        n_groups = 20
        data = new_groups(n_groups)

        for d in data:
            group = StudentGroup.objects.create(**d)
            self.assertIsInstance(group, StudentGroup)
            self.assertEqual(group.name, d["name"])
            self.assertEqual(group.title, d["title"])

    def test_hashing(self):
        n_groups = 20
        groups = add_groups(new_groups(n_groups))

        for group in groups:
            self.assertEqual(group, StudentGroup.get(group.hash))


class TestStudentGroupAssignment(TestCase):
    def setUp(self):
        n_assignments = 20
        n_groups = 2
        n_questions = 100

        questions = add_questions(new_questions(n_questions))
        self.groups = add_groups(new_groups(n_groups))
        self.assignments = add_assignments(
            new_assignments(n_assignments, questions)
        )

    def test_new_student_group_assignment(self):
        n = 10
        data = new_student_group_assignments(n, self.groups, self.assignments)

        for d in data:
            group = StudentGroupAssignment.objects.create(**d)
            self.assertIsInstance(group, StudentGroupAssignment)
            self.assertEqual(group.group, d["group"])
            self.assertEqual(group.assignment, d["assignment"])

    def test_is_expired(self):
        due_dates = [
            datetime.now(pytz.utc),
            datetime.now(pytz.utc) + timedelta(days=1),
        ]
        assignments = add_student_group_assignments(
            reduce(
                add,
                (
                    new_student_group_assignments(
                        1, self.groups, self.assignments, due_date=due_date
                    )
                    for due_date in due_dates
                ),
            )
        )

        self.assertEqual(assignments[0].is_expired(), True)
        self.assertEqual(assignments[1].is_expired(), False)

    def test_hashing(self):
        n = 10
        assignments = add_student_group_assignments(
            new_student_group_assignments(n, self.groups, self.assignments)
        )

        for assignment in assignments:
            self.assertEqual(
                assignment, StudentGroupAssignment.get(assignment.hash)
            )


class TestStudentAssignment(TestCase):
    def setUp(self):
        n_students = 15
        n_assignments = 20
        n_groups = 2
        n_questions = 100
        min_questions = 5
        n_group_assignments = 3

        questions = add_questions(new_questions(n_questions))
        groups = add_groups(new_groups(n_groups))
        assignments = add_assignments(
            new_assignments(
                n_assignments, questions, min_questions=min_questions
            )
        )
        self.students = add_students(new_students(n_students))
        self.groups = add_student_group_assignments(
            new_student_group_assignments(
                n_group_assignments, groups, assignments
            )
        )

    def test_new_student_assignment(self):
        n = 30
        data = new_student_assignments(n, self.groups, self.students)

        for d in data:
            assignment = StudentAssignment.objects.create(**d)
            self.assertIsInstance(assignment, StudentAssignment)
            self.assertEqual(assignment.student, d["student"])
            self.assertEqual(
                assignment.group_assignment, d["group_assignment"]
            )

    def test_get_current_question_no_answers(self):
        n = 1
        assignment = add_student_assignments(
            new_student_assignments(n, self.groups, self.students)
        )[0]
