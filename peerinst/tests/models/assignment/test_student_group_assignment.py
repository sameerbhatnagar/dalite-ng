import random
from datetime import datetime, timedelta
from operator import itemgetter

import pytest
import pytz

from peerinst.models import StudentGroupAssignment
from peerinst.tests.generators import (
    add_answers,
    add_student_group_assignments,
    new_student_group_assignments,
)

from .fixtures import *  # noqa F403


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


@pytest.mark.django_db
def test_get_student_progress_no_questions_done(
    questions, students_with_assignment, student_group_assignment
):
    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == 0
        assert question["first_correct"] == 0
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_some_first_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    times_answered = {
        q.pk: random.randrange(1, len(students_with_assignment))
        for q in questions
    }
    n_correct = {
        q.pk: random.randint(0, times_answered[q.pk]) for q in questions
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct[question.pk]),
                "rationale": "test",
            }
            for question in questions
            for i, student in enumerate(
                students_with_assignment[: times_answered[question.pk]]
            )
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q for q in questions if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == times_answered[question_.pk]
        assert question["first_correct"] == n_correct[question_.pk]
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_all_first_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    n_correct = {
        q.pk: random.randint(0, len(students_with_assignment))
        for q in questions
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct[question.pk]),
                "rationale": "test",
            }
            for question in questions
            for i, student in enumerate(students_with_assignment)
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q for q in questions if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == len(students_with_assignment)
        assert question["first_correct"] == n_correct[question_.pk]
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_some_second_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    times_first_answered = {
        q.pk: random.randrange(2, len(students_with_assignment))
        for q in questions
    }
    n_first_correct = {
        q.pk: random.randint(0, times_first_answered[q.pk]) for q in questions
    }
    times_second_answered = {
        q.pk: random.randrange(1, times_first_answered[q.pk])
        for q in questions
    }
    n_second_correct = {
        q.pk: random.randint(0, times_second_answered[q.pk]) for q in questions
    }
    answers = add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1
                + (
                    i + times_second_answered[question.pk]
                    >= n_first_correct[question.pk]
                ),
                "rationale": "test",
            }
            for question in questions
            for i, student in enumerate(
                students_with_assignment[
                    times_second_answered[question.pk] : times_first_answered[
                        question.pk
                    ]
                ]
            )
        ]
    )
    answers += add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_first_correct[question.pk]),
                "rationale": "test",
                "second_answer_choice": 1
                + (i >= n_second_correct[question.pk]),
                "chosen_rationale": random.choice(
                    [a for a in answers if a.question == question]
                ),
            }
            for question in questions
            for i, student in enumerate(
                students_with_assignment[: times_second_answered[question.pk]]
            )
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q for q in questions if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == times_first_answered[question_.pk]
        assert question["first_correct"] == n_first_correct[question_.pk]
        assert question["second"] == times_second_answered[question_.pk]
        assert question["second_correct"] == n_second_correct[question_.pk]


@pytest.mark.django_db
def test_get_student_progress_all_second_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    n_first_correct = {
        q.pk: random.randint(0, len(students_with_assignment))
        for q in questions
    }
    n_second_correct = {
        q.pk: random.randint(0, len(students_with_assignment))
        for q in questions
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_first_correct[question.pk]),
                "rationale": "test",
                "second_answer_choice": 1
                + (i >= n_second_correct[question.pk]),
                "chosen_rationale": None,
            }
            for question in questions
            for i, student in enumerate(students_with_assignment)
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q for q in questions if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == len(students_with_assignment)
        assert question["first_correct"] == n_first_correct[question_.pk]
        assert question["second"] == len(students_with_assignment)
        assert question["second_correct"] == n_second_correct[question_.pk]


@pytest.mark.django_db
def test_get_student_progress_all_answers_correct_no_questions_all_answers_correct_done(
    questions_all_answers_correct,
    students_with_assignment_all_answers_correct,
    student_group_assignment_all_answers_correct,
):
    progress = (
        student_group_assignment_all_answers_correct.get_student_progress()
    )

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions_all_answers_correct)
    )
    assert not set((q.title for q in questions_all_answers_correct)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        assert len(question["students"]) == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first"] == 0
        assert question["first_correct"] == 0
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_all_answers_correct_some_first_answers_done(
    questions_all_answers_correct,
    students_with_assignment_all_answers_correct,
    student_group_assignment_all_answers_correct,
):
    times_answered = {
        q.pk: random.randrange(
            1, len(students_with_assignment_all_answers_correct)
        )
        for q in questions_all_answers_correct
    }
    n_correct = {
        q.pk: random.randint(0, times_answered[q.pk])
        for q in questions_all_answers_correct
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment_all_answers_correct.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct[question.pk]),
                "rationale": "test",
            }
            for question in questions_all_answers_correct
            for i, student in enumerate(
                students_with_assignment_all_answers_correct[
                    : times_answered[question.pk]
                ]
            )
        ]
    )

    progress = (
        student_group_assignment_all_answers_correct.get_student_progress()
    )

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions_all_answers_correct)
    )
    assert not set((q.title for q in questions_all_answers_correct)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q
            for q in questions_all_answers_correct
            if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first"] == times_answered[question_.pk]
        assert question["first_correct"] == times_answered[question_.pk]
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_all_answers_correct_all_first_answers_done(
    questions_all_answers_correct,
    students_with_assignment_all_answers_correct,
    student_group_assignment_all_answers_correct,
):
    n_correct = {
        q.pk: random.randint(
            0, len(students_with_assignment_all_answers_correct)
        )
        for q in questions_all_answers_correct
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment_all_answers_correct.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_correct[question.pk]),
                "rationale": "test",
            }
            for question in questions_all_answers_correct
            for i, student in enumerate(
                students_with_assignment_all_answers_correct
            )
        ]
    )

    progress = (
        student_group_assignment_all_answers_correct.get_student_progress()
    )

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions_all_answers_correct)
    )
    assert not set((q.title for q in questions_all_answers_correct)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        assert len(question["students"]) == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first"] == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first_correct"] == len(
            students_with_assignment_all_answers_correct
        )
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_all_answers_correct_some_second_answers_done(
    questions_all_answers_correct,
    students_with_assignment_all_answers_correct,
    student_group_assignment_all_answers_correct,
):
    times_first_answered = {
        q.pk: random.randrange(
            2, len(students_with_assignment_all_answers_correct)
        )
        for q in questions_all_answers_correct
    }
    n_first_correct = {
        q.pk: random.randint(0, times_first_answered[q.pk])
        for q in questions_all_answers_correct
    }
    times_second_answered = {
        q.pk: random.randrange(1, times_first_answered[q.pk])
        for q in questions_all_answers_correct
    }
    n_second_correct = {
        q.pk: random.randint(0, times_second_answered[q.pk])
        for q in questions_all_answers_correct
    }
    answers = add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment_all_answers_correct.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1
                + (
                    i + times_second_answered[question.pk]
                    >= n_first_correct[question.pk]
                ),
                "rationale": "test",
            }
            for question in questions_all_answers_correct
            for i, student in enumerate(
                students_with_assignment_all_answers_correct[
                    times_second_answered[question.pk] : times_first_answered[
                        question.pk
                    ]
                ]
            )
        ]
    )
    answers += add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment_all_answers_correct.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_first_correct[question.pk]),
                "rationale": "test",
                "second_answer_choice": 1
                + (i >= n_second_correct[question.pk]),
                "chosen_rationale": random.choice(
                    [a for a in answers if a.question == question]
                ),
            }
            for question in questions_all_answers_correct
            for i, student in enumerate(
                students_with_assignment_all_answers_correct[
                    : times_second_answered[question.pk]
                ]
            )
        ]
    )

    progress = (
        student_group_assignment_all_answers_correct.get_student_progress()
    )

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions_all_answers_correct)
    )
    assert not set((q.title for q in questions_all_answers_correct)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        question_ = next(
            q
            for q in questions_all_answers_correct
            if q.title == question["question_title"]
        )
        assert len(question["students"]) == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first"] == times_first_answered[question_.pk]
        assert question["first_correct"] == times_first_answered[question_.pk]
        assert question["second"] == times_second_answered[question_.pk]
        assert (
            question["second_correct"] == times_second_answered[question_.pk]
        )


@pytest.mark.django_db
def test_get_student_progress_all_answers_correct_all_second_answers_done(
    questions_all_answers_correct,
    students_with_assignment_all_answers_correct,
    student_group_assignment_all_answers_correct,
):
    n_first_correct = {
        q.pk: random.randint(
            0, len(students_with_assignment_all_answers_correct)
        )
        for q in questions_all_answers_correct
    }
    n_second_correct = {
        q.pk: random.randint(
            0, len(students_with_assignment_all_answers_correct)
        )
        for q in questions_all_answers_correct
    }
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment_all_answers_correct.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1 + (i >= n_first_correct[question.pk]),
                "rationale": "test",
                "second_answer_choice": 1
                + (i >= n_second_correct[question.pk]),
                "chosen_rationale": None,
            }
            for question in questions_all_answers_correct
            for i, student in enumerate(
                students_with_assignment_all_answers_correct
            )
        ]
    )

    progress = (
        student_group_assignment_all_answers_correct.get_student_progress()
    )

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions_all_answers_correct)
    )
    assert not set((q.title for q in questions_all_answers_correct)) - set(
        map(itemgetter("question_title"), progress)
    )

    for question in progress:
        assert len(question["students"]) == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first"] == len(
            students_with_assignment_all_answers_correct
        )
        assert question["first_correct"] == len(
            students_with_assignment_all_answers_correct
        )
        assert question["second"] == len(
            students_with_assignment_all_answers_correct
        )
        assert question["second_correct"] == len(
            students_with_assignment_all_answers_correct
        )
