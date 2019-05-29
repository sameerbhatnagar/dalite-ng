# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime

import mock
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from peerinst.tests.fixtures import *  # noqa
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
        reverse("teacher-page--student-activity"),
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
        reverse("teacher-page--new-questions"),
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
        reverse("teacher-page--new-questions"),
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
        reverse("teacher-page--new-questions"),
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
        reverse("teacher-page--new-questions"),
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
            reverse("teacher-page--new-questions"),
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
            reverse("teacher-page--rationales"),
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
            reverse("teacher-page--rationales"),
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
            reverse("teacher-page--rationales"),
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
            reverse("teacher-page--rationales"),
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
            reverse("teacher-page--rationales"),
            json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400
