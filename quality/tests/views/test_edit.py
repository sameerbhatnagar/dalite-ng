import json

import mock
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse

from peerinst.models import StudentGroupAssignment
from peerinst.tests.fixtures import *  # noqa
from quality.models import Quality, QualityType, UsesCriterion
from quality.tests.fixtures import *  # noqa
from quality.views.edit import verify_assignment


def test_verify_assignment(client, rf, student_group_assignment, teacher):
    req = rf.get("/test")
    req.user = teacher.user

    student_group_assignment.group.teacher.add(teacher)

    resp = verify_assignment(req, student_group_assignment.pk)
    assert isinstance(resp, StudentGroupAssignment)
    assert isinstance(
        StudentGroupAssignment.objects.get(
            pk=student_group_assignment.pk
        ).quality,
        Quality,
    )


def test_verify_assignment__assignment_doesnt_exist(client, rf):
    req = rf.get("/test")

    resp = verify_assignment(req, 0)

    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_verify_assignment__teacher_doesnt_exist(
    client, rf, student_group_assignment, user
):
    req = rf.get("/test")
    req.user = user

    resp = verify_assignment(req, student_group_assignment.pk)

    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_verify_assignment__teacher_doesnt_have_access(
    client, rf, student_group_assignment, teacher
):
    req = rf.get("/test")
    req.user = teacher.user

    student_group_assignment.group.teacher.remove(teacher)

    resp = verify_assignment(req, student_group_assignment.pk)

    assert resp.status_code == 403
    assert resp.template_name == "403.html"


def test_index(client, student_group_assignment, teacher):
    student_group_assignment.group.teacher.add(teacher)

    client.login(username=teacher.user.username, password="test")
    resp = client.get(
        "/quality/edit/?assignment={}".format(student_group_assignment.pk),
        follow=True,
    )
    assert resp.status_code == 200
    assert any(t.name == "quality/edit/index.html" for t in resp.templates)


def test_index__missing_pk(client, student_group_assignment, teacher):
    client.login(username=teacher.user.username, password="test")
    resp = client.get("/quality/edit/", follow=True)
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_index__assignment_error(
    client, rf, student_group_assignment, teacher
):
    client.login(username=teacher.user.username, password="test")
    with mock.patch(
        "quality.views.edit.verify_assignment"
    ) as verify_assignment:
        req = rf.get("/test")
        verify_assignment.return_value = TemplateResponse(
            req, "400.html", status=400
        )
        resp = client.get(
            "/quality/edit/?assignment={}".format(student_group_assignment.pk),
            follow=True,
        )
        assert resp.status_code == 400
        assert resp.template_name == "400.html"


def test_add_criterion(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:add-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200


def test_add_criterion__wrong_type(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:add-criterion"),
        "random string",
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_add_criterion__missing_params(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:add-criterion"),
        json.dumps({"quality": student_group_assignment.quality.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:add-criterion"),
        json.dumps({"criterion": min_words_criterion.name}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_add_criterion__wrong_quality_pk(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:add-criterion"),
        json.dumps({"quality": -1, "criterion": min_words_criterion.name}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_add_criterion__wrong_criterion_name(
    client, student_group_assignment, teacher
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:add-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": "fake",
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_update_criterion(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
                "field": "weight",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200


def test_update_criterion__wrong_type(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        "random string",
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_update_criterion__missing_params(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "criterion": min_words_criterion.name,
                "field": "weight",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "field": "weight",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
                "field": "weight",
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_update_criterion__wrong_quality_pk(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": -1,
                "criterion": min_words_criterion.name,
                "field": "weight",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_update_criterion__wrong_criterion(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": "fake",
                "field": "weight",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_update_criterion__wrong_field(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:update-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
                "field": "fake",
                "value": 2,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_remove_criterion(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:remove-criterion"),
        json.dumps(
            {
                "quality": student_group_assignment.quality.pk,
                "criterion": min_words_criterion.name,
            }
        ),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 200


def test_remove_criterion__wrong_type(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:remove-criterion"),
        "random string",
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_remove_criterion__missing_params(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:remove-criterion"),
        json.dumps({"criterion": min_words_criterion.name}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"

    resp = client.post(
        reverse("quality:remove-criterion"),
        json.dumps({"quality": student_group_assignment.quality.pk}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"


def test_remove_criterion__wrong_quality_key(
    client,
    student_group_assignment,
    teacher,
    min_words_criterion,
    min_words_rules,
):
    quality_type = QualityType.objects.get(type="assignment")
    student_group_assignment.quality = Quality.objects.create(
        quality_type=quality_type
    )
    student_group_assignment.save()
    student_group_assignment.group.teacher.add(teacher)
    UsesCriterion.objects.create(
        quality=student_group_assignment.quality,
        name=min_words_criterion.name,
        version=min_words_criterion.version,
        rules=min_words_rules.pk,
        weight=0,
    )
    client.login(username=teacher.user.username, password="test")

    resp = client.post(
        reverse("quality:remove-criterion"),
        json.dumps({"quality": -1, "criterion": min_words_criterion.name}),
        content_type="application/json",
        follow=True,
    )
    assert resp.status_code == 400
    assert resp.template_name == "400.html"
