import json

from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from reputation.models import ReputationType, UsesCriterion
from reputation.tests.fixtures import *  # noqa


def test_index(client, staff):
    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers"))
    assert resp.status_code == 200
    assert any(
        t.name == "analytics/teachers/index.html" for t in resp.templates
    )


def test_get_reputation_criteria_list(
    client, staff, question_liked_criterion, n_questions_criterion
):
    criteria = [question_liked_criterion, n_questions_criterion]
    for criterion in criteria:
        UsesCriterion.objects.create(
            reputation_type=ReputationType.objects.get(type="teacher"),
            name=criterion.name,
            version=criterion.version,
        )

    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers--criteria"))

    assert resp.status_code == 200
    data = json.loads(resp.content)["criteria"]
    assert len(data) == 2
    for criterion in data:
        assert criterion["name"] in [c.name for c in criteria]
        assert "full_name" in criterion
        assert "description" in criterion


def test_get_reputation_criteria_list__no_criteria(client, staff):
    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers--criteria"))

    assert resp.status_code == 200
    data = json.loads(resp.content)["criteria"]
    assert not data


def test_get_teacher_list(client, staff, teachers):
    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers--teachers"))

    assert resp.status_code == 200
    data = json.loads(resp.content)["teachers"]
    assert len(data) == len(teachers)
    for teacher in teachers:
        assert teacher.pk in data


def test_get_teacher_list__no_teachers(client, staff):
    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers--teachers"))

    assert resp.status_code == 200
    data = json.loads(resp.content)["teachers"]
    assert not data


def test_get_teacher_information(
    client, staff, question_liked_criterion, n_questions_criterion, teacher
):
    criteria = [question_liked_criterion, n_questions_criterion]
    for criterion in criteria:
        UsesCriterion.objects.create(
            reputation_type=ReputationType.objects.get(type="teacher"),
            name=criterion.name,
            version=criterion.version,
        )

    client.login(username=teacher.user.username, password="test")
    client.login(username=staff.username, password="test")
    resp = client.get(
        "{}?id={}".format(reverse("analytics:teachers--teacher"), teacher.pk)
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data) == 3
    assert data["username"] == teacher.user.username
    assert isinstance(data["last_login"], str)
    for criterion in data["reputations"]:
        assert criterion["name"] in [c.name for c in criteria]
        assert "reputation" in criterion


def test_get_teacher_information__no_login(
    client, staff, question_liked_criterion, n_questions_criterion, teacher
):
    criteria = [question_liked_criterion, n_questions_criterion]
    for criterion in criteria:
        UsesCriterion.objects.create(
            reputation_type=ReputationType.objects.get(type="teacher"),
            name=criterion.name,
            version=criterion.version,
        )

    client.login(username=staff.username, password="test")
    resp = client.get(
        "{}?id={}".format(reverse("analytics:teachers--teacher"), teacher.pk)
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert len(data) == 3
    assert data["username"] == teacher.user.username
    assert data["last_login"] is None
    for criterion in data["reputations"]:
        assert criterion["name"] in [c.name for c in criteria]
        assert "reputation" in criterion


def test_get_teacher_information__missing_params(client, staff):
    client.login(username=staff.username, password="test")
    resp = client.get(reverse("analytics:teachers--teacher"))

    assert resp.status_code == 400


def test_get_teacher_information__wrong_id(client, staff):
    client.login(username=staff.username, password="test")
    resp = client.get("{}?id=1".format(reverse("analytics:teachers--teacher")))

    assert resp.status_code == 400
