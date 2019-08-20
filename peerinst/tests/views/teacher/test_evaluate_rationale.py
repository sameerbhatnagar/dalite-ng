import json

from django.core.urlresolvers import reverse

from peerinst.models import AnswerAnnotation
from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


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
