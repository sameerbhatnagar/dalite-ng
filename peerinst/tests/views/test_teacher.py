# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime

import mock
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from pinax.forums.models import ThreadSubscription

from peerinst.models import AnswerAnnotation, GradingScheme
from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.question import add_answers
from peerinst.tests.fixtures.teacher import login_teacher


def test_student_activity__no_questions_done(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == 0
        assert assignment["mean_grade"] == 0
        assert assignment["min_grade"] == 0
        assert assignment["max_grade"] == 0
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__all_questions_done_correct_first_and_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all():
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=True,
                correct_second=True,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == len(assignment_.questions)
        assert assignment["mean_grade"] == len(assignment_.questions)
        assert assignment["min_grade"] == len(assignment_.questions)
        assert assignment["max_grade"] == len(assignment_.questions)
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__all_questions_done_correct_first_wrong_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all():
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=True,
                correct_second=False,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == len(assignment_.questions)
        assert (
            assignment["mean_grade"] == float(len(assignment_.questions)) / 2
        )
        assert assignment["min_grade"] == float(len(assignment_.questions)) / 2
        assert assignment["max_grade"] == float(len(assignment_.questions)) / 2
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__all_questions_done_wrong_first_and_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all():
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=False,
                correct_second=False,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == len(assignment_.questions)
        assert assignment["mean_grade"] == 0
        assert assignment["min_grade"] == 0
        assert assignment["max_grade"] == 0
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__some_questions_done_correct_first_and_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all()[::2]:
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=True,
                correct_second=True,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == float(len(students[::2]))
        assert assignment["mean_grade"] == len(assignment_.questions)
        assert assignment["min_grade"] == len(assignment_.questions)
        assert assignment["max_grade"] == len(assignment_.questions)
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__some_questions_done_correct_first_wrong_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all()[::2]:
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=True,
                correct_second=False,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == float(len(students[::2]))
        assert (
            assignment["mean_grade"] == float(len(assignment_.questions)) // 2
        )
        assert (
            assignment["min_grade"] == float(len(assignment_.questions)) // 2
        )
        assert (
            assignment["max_grade"] == float(len(assignment_.questions)) // 2
        )
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_student_activity__some_questions_done_wrong_first_and_second(
    client,
    teacher,
    group,
    students,
    student_group_assignments,
    student_assignments,
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)
    for assignment in student_group_assignments:
        for question in assignment.questions:
            question.grading_scheme = GradingScheme.ADVANCED
            question.save()
        for assignment_ in assignment.studentassignment_set.all()[::2]:
            add_answers(
                student=assignment_.student,
                questions=assignment.questions,
                assignment=assignment.assignment,
                correct_first=False,
                correct_second=False,
            )

    resp = client.post(
        reverse("teacher-dashboard--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.content)["groups"][0]
    assert data["title"] == group.title
    assert data["n_students"] == len(students)
    assert data["new"] is True
    assert len(data["assignments"]) == len(student_group_assignments)
    for assignment, assignment_ in zip(
        data["assignments"], student_group_assignments
    ):
        assert assignment["title"] == assignment_.assignment.title
        assert assignment["n_completed"] == float(len(students[::2]))
        assert assignment["mean_grade"] == 0
        assert assignment["min_grade"] == 0
        assert assignment["max_grade"] == 0
        assert assignment["new"] is True
        assert assignment["expired"] is False
        assert assignment["link"].endswith(assignment_.hash + "/")


def test_collections(client, collections, teachers, discipline):
    teacher = teachers[0]
    teachers = teachers[1:]

    teacher.disciplines.add(discipline)

    assert login_teacher(client, teacher)

    for i, collection in enumerate(collections):
        collection.followers.remove(*teachers[: -i - 1])

    resp = client.post(
        reverse("teacher-dashboard--collections"),
        json.dumps({}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["collections"]) == len(collections)

    for collection, collection_ in zip(
        data["collections"], reversed(collections)
    ):
        assert collection["title"] == collection_.title
        assert collection["description"] == collection_.description
        assert collection["discipline"] == collection_.discipline.title
        assert collection["n_assignments"] == collection_.assignments.count()
        assert collection["n_followers"] == collection_.followers.count()


def test_collections__with_params(client, collections, teachers, discipline):
    teacher = teachers[0]
    teachers = teachers[1:]

    teacher.disciplines.add(discipline)

    assert login_teacher(client, teacher)

    for i, collection in enumerate(collections):
        collection.followers.remove(*teachers[: -i - 1])

    resp = client.post(
        reverse("teacher-dashboard--collections"),
        json.dumps({"n": 1}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["collections"]) == 1

    for collection, collection_ in zip(
        data["collections"], reversed(collections)
    ):
        assert collection["title"] == collection_.title
        assert collection["description"] == collection_.description
        assert collection["discipline"] == collection_.discipline.title
        assert collection["n_assignments"] == collection_.assignments.count()
        assert collection["n_followers"] == collection_.followers.count()


def test_collections__wrong_params(client, teachers):
    assert login_teacher(client, teachers[0])

    with mock.patch(
        "peerinst.views.teacher.get_json_params",
        return_value=HttpResponse("", status=400),
    ):
        resp = client.post(
            reverse("teacher-dashboard--new-questions"),
            json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400


def test_new_questions(client, teacher, questions, assignment, disciplines):
    assert login_teacher(client, teacher)

    for question in questions[: len(questions) // 2]:
        question.discipline = disciplines[0]
        question.save()
    for question in questions[len(questions) // 2 :]:
        question.discipline = disciplines[1]
        question.save()

    teacher.disciplines.add(disciplines[0])

    resp = client.post(
        reverse("teacher-dashboard--new-questions"),
        json.dumps({}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == len(questions) // 2

    for i, (question, question_) in enumerate(
        zip(reversed(questions[: len(questions) // 2]), data["questions"])
    ):
        assert question_["title"] == question.title
        assert question_["text"] == question.text
        assert question_["author"] == teacher.user.username
        assert question_["question_type"] == "Peer instruction"
        assert question_[
            "discipline"
        ] in teacher.disciplines.all().values_list("title", flat=True)
        assert question_["n_assignments"] == 1
        for q in data["questions"][i + 1 :]:
            assert datetime.strptime(
                question_["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) >= datetime.strptime(q["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ")


def test_new_questions__with_params(
    client, teacher, questions, assignment, disciplines
):
    assert login_teacher(client, teacher)

    for question in questions[: len(questions) // 2]:
        question.discipline = disciplines[0]
        question.save()
    for question in questions[len(questions) // 2 :]:
        question.discipline = disciplines[1]
        question.save()

    teacher.disciplines.add(disciplines[0])

    resp = client.post(
        reverse("teacher-dashboard--new-questions"),
        json.dumps({"n": 2}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == 2

    for i, (question, question_) in enumerate(
        zip(
            reversed(questions[len(questions) - 2 : len(questions) // 2]),
            data["questions"],
        )
    ):
        assert question_["title"] == question.title
        assert question_["text"] == question.text
        assert question_["author"] == teacher.user.username
        assert question_["question_type"] == "Peer instruction"
        assert question_[
            "discipline"
        ] in teacher.disciplines.all().values_list("title", flat=True)
        assert question_["n_assignments"] == 1
        for q in data["questions"][i + 1 :]:
            assert datetime.strptime(
                question_["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) >= datetime.strptime(q["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ")

    resp = client.post(
        reverse("teacher-dashboard--new-questions"),
        json.dumps(
            {
                "current": [
                    q.pk
                    for q in questions[
                        len(questions) // 2 - 2 : len(questions) // 2
                    ]
                ]
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == len(questions) // 2 - 2

    for i, (question, question_) in enumerate(
        zip(reversed(questions[: len(questions) // 2 - 2]), data["questions"])
    ):
        assert question_["title"] == question.title
        assert question_["text"] == question.text
        assert question_["author"] == teacher.user.username
        assert question_["question_type"] == "Peer instruction"
        assert question_[
            "discipline"
        ] in teacher.disciplines.all().values_list("title", flat=True)
        assert question_["n_assignments"] == 1
        for q in data["questions"][i + 1 :]:
            assert datetime.strptime(
                question_["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) >= datetime.strptime(q["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ")

    resp = client.post(
        reverse("teacher-dashboard--new-questions"),
        json.dumps(
            {
                "n": 2,
                "current": [
                    q.pk
                    for q in questions[
                        len(questions) // 2 - 2 : len(questions) // 2
                    ]
                ],
            }
        ),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == 2

    for i, (question, question_) in enumerate(
        zip(reversed(questions[: len(questions) // 2 - 2]), data["questions"])
    ):
        assert question_["title"] == question.title
        assert question_["text"] == question.text
        assert question_["author"] == teacher.user.username
        assert question_["question_type"] == "Peer instruction"
        assert question_[
            "discipline"
        ] in teacher.disciplines.all().values_list("title", flat=True)
        assert question_["n_assignments"] == 1
        for q in data["questions"][i + 1 :]:
            assert datetime.strptime(
                question_["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) >= datetime.strptime(q["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ")


def test_new_questions__wrong_params(client, teacher):
    assert login_teacher(client, teacher)

    with mock.patch(
        "peerinst.views.teacher.get_json_params",
        return_value=HttpResponse("", status=400),
    ):
        resp = client.post(
            reverse("teacher-dashboard--new-questions"),
            json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400


def test_rationales_to_score(client, teacher, answers, discipline):
    teacher.disciplines.add(discipline)
    for i, answer in enumerate(answers):
        answer.question.discipline = discipline
        answer.question.save()

    assert login_teacher(client, teacher)

    with mock.patch("peerinst.rationale_annotation.Quality") as Quality:
        qualities = [float(i) / len(answers) for i in range(len(answers))]
        Quality.objects.filter.return_value.exists.return_value = True
        Quality.objects.get.return_value.batch_evaluate.return_value = [
            (q, None) for q in qualities
        ]

        resp = client.post(
            reverse("teacher-dashboard--rationales"),
            json.dumps({}),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert len(data["rationales"]) == 5

        for a, a_ in zip(data["rationales"], answers[::-1]):
            assert a["id"] == a_.pk
            assert a["title"] == a_.question.title
            assert a["rationale"] == a_.rationale
            assert a["choice"] == a_.first_answer_choice
            assert (
                a["text"]
                == a_.question.answerchoice_set.all()[
                    a_.first_answer_choice - 1
                ].text
            )
            assert a["correct"] == a_.question.is_correct(
                a_.first_answer_choice
            )


def test_rationales_to_score__with_params(
    client, teacher, answers, discipline
):
    teacher.disciplines.add(discipline)
    for i, answer in enumerate(answers):
        answer.question.discipline = discipline
        answer.question.save()

    assert login_teacher(client, teacher)

    with mock.patch("peerinst.rationale_annotation.Quality") as Quality:
        qualities = [float(i) / len(answers) for i in range(len(answers))]
        Quality.objects.filter.return_value.exists.return_value = True
        Quality.objects.get.return_value.batch_evaluate.return_value = [
            (q, None) for q in qualities
        ]

        resp = client.post(
            reverse("teacher-dashboard--rationales"),
            json.dumps({"n": 3}),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert len(data["rationales"]) == 3

        for a, a_ in zip(data["rationales"], answers[::-1]):
            assert a["id"] == a_.pk
            assert a["title"] == a_.question.title
            assert a["rationale"] == a_.rationale
            assert a["choice"] == a_.first_answer_choice
            assert (
                a["text"]
                == a_.question.answerchoice_set.all()[
                    a_.first_answer_choice - 1
                ].text
            )
            assert a["correct"] == a_.question.is_correct(
                a_.first_answer_choice
            )

        resp = client.post(
            reverse("teacher-dashboard--rationales"),
            json.dumps({"current": [a.pk for a in answers[-3:]]}),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert len(data["rationales"]) == 5

        for a, a_ in zip(data["rationales"], answers[:-3][::-1]):
            assert a["id"] == a_.pk
            assert a["title"] == a_.question.title
            assert a["rationale"] == a_.rationale
            assert a["choice"] == a_.first_answer_choice
            assert (
                a["text"]
                == a_.question.answerchoice_set.all()[
                    a_.first_answer_choice - 1
                ].text
            )
            assert a["correct"] == a_.question.is_correct(
                a_.first_answer_choice
            )

        resp = client.post(
            reverse("teacher-dashboard--rationales"),
            json.dumps({"n": 3, "current": [a.pk for a in answers[-3:]]}),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert len(data["rationales"]) == 3

        for a, a_ in zip(data["rationales"], answers[:-3][::-1]):
            assert a["id"] == a_.pk
            assert a["title"] == a_.question.title
            assert a["rationale"] == a_.rationale
            assert a["choice"] == a_.first_answer_choice
            assert (
                a["text"]
                == a_.question.answerchoice_set.all()[
                    a_.first_answer_choice - 1
                ].text
            )
            assert a["correct"] == a_.question.is_correct(
                a_.first_answer_choice
            )


def test_rationales_to_score__wrong_params(client, teacher):
    assert login_teacher(client, teacher)

    with mock.patch(
        "peerinst.views.teacher.get_json_params",
        return_value=HttpResponse("", status=400),
    ):
        resp = client.post(
            reverse("teacher-dashboard--rationales"),
            json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400


def test_messages(client, teacher, thread):
    assert login_teacher(client, teacher)

    replies = thread.replies.order_by("-created").all()
    teacher.last_dashboard_access = replies[len(replies) // 2].created
    teacher.save()

    resp = client.post(reverse("teacher-dashboard--messages"))
    assert resp.status_code == 200
    data = json.loads(resp.content)["threads"]

    assert len(data) == 1
    for thread in data:
        assert "id" in thread
        assert "last_reply" in thread
        assert "author" in thread["last_reply"]
        assert "content" in thread["last_reply"]
        assert thread["n_new"] == len(replies) // 2

        resp = client.get(thread["link"])
        assert resp.status_code == 200
        assert "pinax/forums/thread.html" in resp.template_name


def test_unsubscribe_from_thread(client, teacher, thread):
    assert login_teacher(client, teacher)
    assert ThreadSubscription.objects.filter(
        user=teacher.user, thread=thread
    ).count()

    resp = client.post(
        reverse("teacher-dashboard--unsubscribe-thread"),
        json.dumps({"id": thread.pk}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert not ThreadSubscription.objects.filter(
        user=teacher.user, thread=thread
    ).count()


def test_unsubscribe_from_thread__missing_params(client, teacher, thread):
    assert login_teacher(client, teacher)
    assert ThreadSubscription.objects.filter(
        user=teacher.user, thread=thread
    ).count()

    resp = client.post(
        reverse("teacher-dashboard--unsubscribe-thread"),
        json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert ThreadSubscription.objects.filter(
        user=teacher.user, thread=thread
    ).count()


def test_evaluate_rationale(client, teacher, answers):
    answer = answers[0]

    assert login_teacher(client, teacher)

    n = AnswerAnnotation.objects.count()

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": answer.pk, "score": 0}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    assert AnswerAnnotation.objects.count() == n + 1


def test_evaluate_rationale__missing_params(client, teacher, answers):
    answer = answers[0]

    assert login_teacher(client, teacher)

    n = AnswerAnnotation.objects.count()

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": answer.pk}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"score": 0}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n


def test_evaluate_rationale__wrong_answer_pk(client, teacher):
    assert login_teacher(client, teacher)

    n = AnswerAnnotation.objects.count()

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": 0, "score": 0}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n


def test_evaluate_rationale__wrong_score(client, teacher, answers):
    answer = answers[0]

    assert login_teacher(client, teacher)

    n = AnswerAnnotation.objects.count()

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": 0, "score": 4}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": 0, "score": -1}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n

    resp = client.post(
        reverse("teacher-dashboard--evaluate-rationale"),
        json.dumps({"id": 0, "score": "0"}),
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert AnswerAnnotation.objects.count() == n
