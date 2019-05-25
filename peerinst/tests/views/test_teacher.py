# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime

import mock
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


def test_student_activity(client, teacher, group, student_assignments):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)

    resp = client.post(
        reverse("teacher-page--student-activity"),
        json.dumps({}),
        content_type="application/json",
    )


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
        json.dumps({"question_index": 1}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == len(questions) // 2 - 1

    for i, (question, question_) in enumerate(
        zip(reversed(questions[: len(questions) // 2 - 1]), data["questions"])
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
        json.dumps({"n_questions": 2}),
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
        json.dumps({"question_index": 1, "n_questions": 2}),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data["questions"]) == 2

    for i, (question, question_) in enumerate(
        zip(
            reversed(questions[len(questions) - 3 : len(questions) // 2 - 1]),
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
