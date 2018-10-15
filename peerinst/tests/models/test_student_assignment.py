import random
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from django.test import TestCase

from peerinst.models import StudentAssignment
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


class TestNewStudentAssignment(TestCase):
    def setUp(self):
        questions = add_questions(new_questions(10))
        groups = add_groups(new_groups(2))
        assignments = add_assignments(
            new_assignments(3, questions, min_questions=10)
        )
        self.students = add_students(new_students(5))
        self.groups = add_student_group_assignments(
            new_student_group_assignments(3, groups, assignments)
        )

    def test_new_student_assignment(self):
        n = len(self.groups) * len(self.students)
        data = new_student_assignments(n, self.groups, self.students)

        for d in data:
            assignment = StudentAssignment.objects.create(**d)
            self.assertIsInstance(assignment, StudentAssignment)
            self.assertEqual(assignment.student, d["student"])
            self.assertEqual(
                assignment.group_assignment, d["group_assignment"]
            )


class TestGetCurrentQuestion(TestCase):
    def setUp(self):
        questions = add_questions(new_questions(10))
        groups = add_groups(new_groups(1))
        assignments = add_assignments(
            new_assignments(1, questions, min_questions=10)
        )
        students = add_students(new_students(1))
        assignments = add_student_group_assignments(
            new_student_group_assignments(1, groups, assignments)
        )
        self.assignment = add_student_assignments(
            new_student_assignments(1, assignments, students)
        )[0]

    def test_no_answers(self):
        questions = self.assignment.group_assignment.questions

        question = self.assignment.get_current_question()
        self.assertEqual(question, questions[0])

        for _ in range(5):
            new_order = ",".join(
                map(
                    str, random.sample(range(len(questions)), k=len(questions))
                )
            )
            self.assignment.group_assignment.modify_order(new_order)
            questions = self.assignment.group_assignment.questions
            question = self.assignment.get_current_question()
            self.assertEqual(question, questions[0])

    def test_some_first_answers_done(self):
        student = self.assignment.student
        questions = self.assignment.group_assignment.questions
        n_done = random.randrange(1, len(questions))
        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.group_assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in questions[:n_done]
            ]
        )

        question = self.assignment.get_current_question()
        self.assertEqual(question, questions[n_done])

    def test_all_first_answers_done(self):
        student = self.assignment.student
        questions = self.assignment.group_assignment.questions
        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.group_assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in questions
            ]
        )

        question = self.assignment.get_current_question()
        self.assertEqual(question, questions[0])

    def test_some_second_answers_done(self):
        student = self.assignment.student
        questions = self.assignment.group_assignment.questions
        n_second = random.randrange(1, len(questions))
        answers = add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.group_assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                }
                for question in questions[n_second:]
            ]
        )
        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.group_assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                    "second_answer_choice": 1,
                    "chosen_rationale": None,
                }
                for question in questions[:n_second]
            ]
        )

        question = self.assignment.get_current_question()
        self.assertEqual(question, questions[n_second])

    def test_all_second_answers_done(self):
        student = self.assignment.student
        questions = self.assignment.group_assignment.questions

        add_answers(
            [
                {
                    "question": question,
                    "assignment": self.assignment.group_assignment.assignment,
                    "user_token": student.student.username,
                    "first_answer_choice": 1,
                    "rationale": "test",
                    "second_answer_choice": 1,
                    "chosen_rationale": None,
                }
                for question in questions
            ]
        )

        question = self.assignment.get_current_question()
        self.assertIs(question, None)
