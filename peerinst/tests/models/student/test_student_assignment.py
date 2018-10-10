import random

import pytest

from peerinst.models import StudentAssignment
from peerinst.tests.generators import (
    add_answers,
    add_assignments,
    add_groups,
    add_questions,
    add_student_assignments,
    add_student_group_assignments,
    add_students,
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


@pytest.fixture
def group_assignment():
    group = add_groups(new_groups(1))
    questions = add_questions(new_questions(10))
    assignment = add_assignments(
        new_assignments(1, questions, min_questions=10)
    )
    return add_student_group_assignments(
        new_student_group_assignments(1, group, assignment)
    )[0]


@pytest.fixture
def assignment(student, group_assignment):
    return add_student_assignments(
        new_student_assignments(1, group_assignment, student)
    )[0]


@pytest.mark.django_db
def test_new_student_assignment(student, group_assignment):
    data = new_student_assignments(1, group_assignment, student)[0]

    assignment = StudentAssignment.objects.create(**data)
    assert isinstance(assignment, StudentAssignment)
    assert assignment.student == student
    assert assignment.group_assignment == group_assignment


@pytest.mark.django_db
def test_get_current_question_no_answers(assignment):
    questions = assignment.group_assignment.questions

    question = assignment.get_current_question()
    assert question == questions[0]

    for _ in range(5):
        new_order = ",".join(
            map(str, random.sample(range(len(questions)), k=len(questions)))
        )
        assignment.group_assignment.modify_order(new_order)
        questions = assignment.group_assignment.questions
        question = assignment.get_current_question()
        assert question == questions[0]


@pytest.mark.django_db
def test_get_current_question_some_first_answers_done(assignment):
    student = assignment.student
    questions = assignment.group_assignment.questions
    n_done = random.randrange(1, len(questions))
    add_answers(
        [
            {
                "question": question,
                "assignment": assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions[:n_done]
        ]
    )

    question = assignment.get_current_question()
    assert question == questions[n_done]


@pytest.mark.django_db
def test_get_current_question_all_first_answers_done(assignment):
    student = assignment.student
    questions = assignment.group_assignment.questions
    add_answers(
        [
            {
                "question": question,
                "assignment": assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions
        ]
    )

    question = assignment.get_current_question()
    assert question == questions[0]


@pytest.mark.django_db
def test_get_current_question_some_second_answers_done(assignment):
    student = assignment.student
    questions = assignment.group_assignment.questions
    n_second = random.randrange(1, len(questions))
    add_answers(
        [
            {
                "question": question,
                "assignment": assignment.group_assignment.assignment,
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
                "assignment": assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions[:n_second]
        ]
    )

    question = assignment.get_current_question()
    assert question == questions[n_second]


@pytest.mark.django_db
def test_get_current_question_all_second_answers_done(assignment):
    student = assignment.student
    questions = assignment.group_assignment.questions

    add_answers(
        [
            {
                "question": question,
                "assignment": assignment.group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions
        ]
    )

    question = assignment.get_current_question()
    assert question is None


@pytest.mark.django_db
def test_get_results_no_answers(assignment):
    #  correct = {
    #  "first_answered": 0,
    #  "second_answered": 0,
    #  "first_correct": 0,
    #  "second_correct": 0,
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_all_answered_correct(assignment, n=5):
    #  correct = {
    #  "first_answered": n,
    #  "second_answered": n,
    #  "first_correct": n,
    #  "second_correct": n,
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_some_answered_correct_second(assignment, n=5):
    #  n_second = random.randint(1, n - 1)
    #  correct = {
    #  "first_answered": n,
    #  "second_answered": n_second,
    #  "first_correct": 0,
    #  "second_correct": random.randint(1, n_second),
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_some_answered_correct_first_and_second(assignment, n=5):
    #  n_first = random.randint(1, n - 1)
    #  n_second = random.randint(1, n_first)
    #  correct = {
    #  "first_answered": n_first,
    #  "second_answered": n_second,
    #  "first_correct": random.randint(1, n_first),
    #  "second_correct": random.randint(1, n_second),
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_all_answered_correct_first_and_none_second(
    assignment, n=5
):
    #  n_first = random.randint(1, n - 1)
    #  n_second = random.randint(1, n_first)
    #  correct = {
    #  "first_answered": n_first,
    #  "second_answered": n_second,
    #  "first_correct": n_first,
    #  "second_correct": 0,
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_none_answered_correct_first_and_all_second(
    assignment, n=5
):
    #  n_first = random.randint(1, n - 1)
    #  n_second = random.randint(1, n_first)
    #  correct = {
    #  "first_answered": n_first,
    #  "second_answered": n_second,
    #  "first_correct": 0,
    #  "second_correct": n_second,
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass


@pytest.mark.django_db
def test_get_results_none_answered_correct_first_and_second(assignment, n=5):
    #  n_first = random.randint(1, n - 1)
    #  n_second = random.randint(1, n_first)
    #  correct = {
    #  "first_answered": n_first,
    #  "second_answered": n_second,
    #  "first_correct": 0,
    #  "second_correct": 0,
    #  }
    #
    #  result = assignment.get_results()
    #  assert result == correct
    pass
