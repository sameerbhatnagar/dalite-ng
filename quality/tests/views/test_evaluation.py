import json

from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from quality.models import Quality, UsesCriterion
from quality.tests.fixtures import *  # noqa


def test_evaluate_rationale(
    client, teacher, min_words_criterion, min_words_rules, answers
):
    quality = Quality.objects.get(
        quality_type__type="global", quality_use_type__type="evaluation"
    )
    min_words_rules.min_words = 3
    min_words_rules.save()
    UsesCriterion.objects.create(
        quality=quality,
        name="min_words",
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=1,
    )
    answer = answers[0]
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({"answer": answer.pk, "quality": quality.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data
    assert len(data) == 2
    assert "quality" in data
    assert "evaluation" in data


def test_evaluate_rationale__wrong_type(client, teacher):
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:evaluate"),
        "fake",
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_evaluate_rationale__missing_params(client, teacher, answers):
    quality = Quality.objects.get(
        quality_type__type="global", quality_use_type__type="evaluation"
    )
    answer = answers[0]
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({"quality": quality.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({"answer": answer.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_evaluate_rationale__wrong_answer_pk(client, teacher):
    quality = Quality.objects.get(
        quality_type__type="global", quality_use_type__type="evaluation"
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({"quality": quality.pk, "answer": 0}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_evaluate_rationale__wrong_quality_pk(client, teacher, answers):
    answer = answers[0]
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:evaluate"),
        json.dumps({"quality": 0, "answer": answer.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"
