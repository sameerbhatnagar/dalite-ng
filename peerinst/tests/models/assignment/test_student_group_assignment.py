import random
from datetime import datetime, timedelta
from operator import itemgetter

import pytest
import pytz

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


@pytest.fixture()
def questions():
    questions = add_questions(new_questions(10))
    add_answer_choices(2, questions)
    return questions


@pytest.fixture
def assignment(questions):
    return add_assignments(
        new_assignments(1, questions, min_questions=len(questions))
    )[0]


@pytest.fixture
def student_group_assignment(group, assignment):
    return add_student_group_assignments(
        new_student_group_assignments(1, group, assignment)
    )[0]


@pytest.fixture
def students_with_assignment(student_group_assignment):
    students = add_students(new_students(20))
    add_to_group(students, student_group_assignment.group)
    add_student_assignments(
        new_student_assignments(
            len(students), student_group_assignment, students
        )
    )
    return students


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
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions
            for student in students_with_assignment[
                : times_answered[question.pk]
            ]
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
        assert question["first_correct"] == times_answered[question_.pk]
        assert question["second"] == 0
        assert question["second_correct"] == 0


@pytest.mark.django_db
def test_get_student_progress_all_first_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions
            for student in students_with_assignment
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )
    print(progress)

    for question in progress:
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == len(students_with_assignment)
        assert question["first_correct"] == len(students_with_assignment)
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
    times_second_answered = {
        q.pk: random.randrange(1, times_first_answered[q.pk])
        for q in questions
    }
    answers = add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
            }
            for question in questions
            for student in students_with_assignment[
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
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": random.choice(
                    [a for a in answers if a.question == question]
                ),
            }
            for question in questions
            for student in students_with_assignment[
                : times_second_answered[question.pk]
            ]
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
        assert question["first_correct"] == times_first_answered[question_.pk]
        assert question["second"] == times_second_answered[question_.pk]
        assert (
            question["second_correct"] == times_second_answered[question_.pk]
        )


@pytest.mark.django_db
def test_get_student_progress_all_second_answers_done(
    questions, students_with_assignment, student_group_assignment
):
    add_answers(
        [
            {
                "question": question,
                "assignment": student_group_assignment.assignment,
                "user_token": student.student.username,
                "first_answer_choice": 1,
                "rationale": "test",
                "second_answer_choice": 1,
                "chosen_rationale": None,
            }
            for question in questions
            for student in students_with_assignment
        ]
    )

    progress = student_group_assignment.get_student_progress()

    assert not set(map(itemgetter("question_title"), progress)) - set(
        (q.title for q in questions)
    )
    assert not set((q.title for q in questions)) - set(
        map(itemgetter("question_title"), progress)
    )
    print(progress)

    for question in progress:
        assert len(question["students"]) == len(students_with_assignment)
        assert question["first"] == len(students_with_assignment)
        assert question["first_correct"] == len(students_with_assignment)
        assert question["second"] == len(students_with_assignment)
        assert question["second_correct"] == len(students_with_assignment)
