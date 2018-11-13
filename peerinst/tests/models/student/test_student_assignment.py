import random

import pytest

from peerinst.models import StudentAssignment
from peerinst.tests.generators import add_answers, new_student_assignments
from .fixtures import *  # noqa F403


@pytest.mark.django_db
def test_new_student_assignment(student, group_assignment):
    data = new_student_assignments(1, group_assignment, student)[0]

    assignment = StudentAssignment.objects.create(**data)
    assert isinstance(assignment, StudentAssignment)
    assert assignment.student == student
    assert assignment.group_assignment == group_assignment


@pytest.mark.django_db
def test_get_current_question_no_answers(student_assignment):
    questions = student_assignment.group_assignment.questions

    question = student_assignment.get_current_question()
    assert question == questions[0]

    for _ in range(5):
        new_order = ",".join(
            map(str, random.sample(range(len(questions)), k=len(questions)))
        )
        student_assignment.group_assignment._modify_order(new_order)
        questions = student_assignment.group_assignment.questions
        question = student_assignment.get_current_question()
        assert question == questions[0]


@pytest.mark.django_db
def test_get_current_question_some_first_answers_done(student_assignment):
    student = student_assignment.student
    questions = student_assignment.group_assignment.questions
    n_done = random.randrange(1, len(questions))
    add_answers(
        [
            {
                "question": question,
                "assignment": student_assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions[:n_done]
        ]
    )

    question = student_assignment.get_current_question()
    assert question == questions[n_done]


@pytest.mark.django_db
def test_get_current_question_all_first_answers_done(student_assignment):
    student = student_assignment.student
    questions = student_assignment.group_assignment.questions
    add_answers(
        [
            {
                "question": question,
                "assignment": student_assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions
        ]
    )

    question = student_assignment.get_current_question()
    assert question == questions[0]


@pytest.mark.django_db
def test_get_current_question_some_second_answers_done(student_assignment):
    student = student_assignment.student
    questions = student_assignment.group_assignment.questions
    n_second = random.randrange(1, len(questions))
    add_answers(
        [
            {
                "question": question,
                "assignment": student_assignment.group_assignment.assignment,
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
                "assignment": student_assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions[:n_second]
        ]
    )

    question = student_assignment.get_current_question()
    assert question == questions[n_second]


@pytest.mark.django_db
def test_get_current_question_all_second_answers_done(student_assignment):
    student = student_assignment.student
    questions = student_assignment.group_assignment.questions

    add_answers(
        [
            {
                "question": question,
                "assignment": student_assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions
        ]
    )

    question = student_assignment.get_current_question()
    assert question is None


@pytest.mark.django_db
def test_get_results_no_answers(student_assignment):
    n = student_assignment.group_assignment.assignment.questions.count()

    correct = {
        "n_first_answered": 0,
        "n_second_answered": 0,
        "n_first_correct": 0,
        "n_second_correct": 0,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_all_answered_correct(student_assignment):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions
        ]
    )

    correct = {
        "n_first_answered": n,
        "n_second_answered": n,
        "n_first_correct": n,
        "n_second_correct": n,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_some_answered_correct_second(student_assignment):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)
    n_second = random.randint(1, n - 1)
    n_correct_second = random.randint(1, n_second)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
            }
            for i, question in enumerate(questions[n_second:])
        ]
        + [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
                "second_answer_choice": 1 + (i >= n_correct_second),
                "chosen_rationale": None,
            }
            for i, question in enumerate(questions[:n_second])
        ]
    )
    correct = {
        "n_first_answered": n,
        "n_second_answered": n_second,
        "n_first_correct": 0,
        "n_second_correct": n_correct_second,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_some_answered_correct_first_and_second(
    student_assignment
):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)
    n_first = random.randint(1, n - 1)
    n_second = random.randint(1, n_first)
    n_correct_first = random.randint(1, n_first)
    n_correct_second = random.randint(1, n_second)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct_first),
                "rationale": "test",
                "second_answer_choice": 1 + (i >= n_correct_second),
                "chosen_rationale": None,
            }
            for i, question in enumerate(questions[:n_second])
        ]
        + [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct_first - n_second),
                "rationale": "test",
            }
            for i, question in enumerate(questions[n_second:n_first])
        ]
    )
    correct = {
        "n_first_answered": n_first,
        "n_second_answered": n_second,
        "n_first_correct": n_correct_first,
        "n_second_correct": n_correct_second,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_all_answered_correct_first_and_none_second(
    student_assignment
):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)
    n_first = random.randint(1, n - 1)
    n_second = random.randint(1, n_first)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 2,
                "chosen_rationale": None,
            }
            for i, question in enumerate(questions[:n_second])
        ]
        + [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for i, question in enumerate(questions[n_second:n_first])
        ]
    )
    correct = {
        "n_first_answered": n_first,
        "n_second_answered": n_second,
        "n_first_correct": n_first,
        "n_second_correct": 0,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_none_answered_correct_first_and_all_second(
    student_assignment
):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)
    n_first = random.randint(1, n - 1)
    n_second = random.randint(1, n_first)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for i, question in enumerate(questions[:n_second])
        ]
        + [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
            }
            for i, question in enumerate(questions[n_second:n_first])
        ]
    )
    correct = {
        "n_first_answered": n_first,
        "n_second_answered": n_second,
        "n_first_correct": 0,
        "n_second_correct": n_second,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct


@pytest.mark.django_db
def test_get_results_none_answered_correct_first_and_second(
    student_assignment
):
    assignment = student_assignment.group_assignment.assignment
    questions = assignment.questions.all()
    student = student_assignment.student
    n = len(questions)
    n_first = random.randint(1, n - 1)
    n_second = random.randint(1, n_first)

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
                "second_answer_choice": 2,
                "chosen_rationale": None,
            }
            for i, question in enumerate(questions[:n_second])
        ]
        + [
            {
                "question": question,
                "assignment": assignment,
                "user_token": student.student.username,
                "first_answer_choice": 2,
                "rationale": "test",
            }
            for i, question in enumerate(questions[n_second:n_first])
        ]
    )
    correct = {
        "n_first_answered": n_first,
        "n_second_answered": n_second,
        "n_first_correct": 0,
        "n_second_correct": 0,
        "n": n,
    }

    result = student_assignment.get_results()
    assert result == correct
