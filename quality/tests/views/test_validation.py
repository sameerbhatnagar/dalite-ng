import json

from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from quality.models import (
    Quality,
    QualityType,
    QualityUseType,
    RejectedAnswer,
    UsesCriterion,
)
from quality.tests.fixtures import *  # noqa


def test_validate_rationale(client, student_group_assignment, teacher):
    quality_type = QualityType.objects.get(type="studentgroupassignment")
    quality_use_type = QualityUseType.objects.get(type="validation")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type, quality_use_type=quality_use_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:validate"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "rationale": "test",
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert not data


def test_validate_rationale__no_quality(client, teacher):
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:validate"),
        json.dumps({"rationale": "test"}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert not data


def test_validate_rationale__failed(
    client, teacher, min_words_criterion, min_words_rules
):
    quality = Quality.objects.get(
        quality_type__type="global", quality_use_type__type="validation"
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
    client.login(username=teacher.user.username, password="test")
    n = RejectedAnswer.objects.count()

    resp = client.post(
        reverse("quality:validate"),
        json.dumps({"rationale": "test"}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data
    assert len(data) == 1
    assert RejectedAnswer.objects.count() == n + 1


def test_validate_rationale__failed_global_and_specific(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="studentgroupassignment")
    quality_use_type = QualityUseType.objects.get(type="validation")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type, quality_use_type=quality_use_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    global_quality = Quality.objects.get(
        quality_type__type="global", quality_use_type__type="validation"
    )
    min_words_rules.min_words = 3
    min_words_rules.save()
    UsesCriterion.objects.create(
        quality=global_quality,
        name="min_words",
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=1,
    )
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name="min_words",
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=1,
    )
    client.login(username=teacher.user.username, password="test")
    n = RejectedAnswer.objects.count()

    resp = client.post(
        reverse("quality:validate"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "rationale": "test",
            }
        ),
        content_type="application/json",
        follow=True,
    )

    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data
    assert len(data) == 1
    assert RejectedAnswer.objects.count() == n + 2


def test_validate_rationale__wrong_type(client, teacher):
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:validate"),
        "fake",
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_validate_rationale__missing_params(client, teacher):
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:validate"),
        json.dumps({}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_validate_rationale__wrong_quality_pk(client, teacher):
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:validate"),
        json.dumps({"quality": 0, "rationale": "test"}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"
