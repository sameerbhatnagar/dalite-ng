import json
import mock
import pytest

from django.urls import reverse
from rest_framework import status

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher
from peerinst.tests.fixtures.student import login_student


@pytest.mark.django_db
def test_assignment_list(client, assignments, teacher):
    """
    Requirements:
    1. Must be authenticated
    2. Must be owner to GET own list
    3. No one can POST
    """

    # Setup
    assert teacher.user.assignment_set.exists() is False
    assignments[0].owner.add(teacher.user)

    # 1. Must be authenticated
    url = reverse("REST:assignment-list") + "?format=json"

    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 2. Must be owner to GET own list
    assert login_teacher(client, teacher)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    retrieved_assignments = json.loads(response.content)
    assert len(retrieved_assignments) == 1
    assert retrieved_assignments[0]["title"] == assignments[0].title

    # 3. No one can POST
    response = client.post(
        url, {"title": "New assignment", "identifier": "UNIQUE"}, format="json"
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_assignment_detail(client, assignments, questions, teacher):
    """
    Requirements:
    1. Must be authenticated
    2. Must be owner to GET
    3. Must be owner to PATCH
    4. No one can DELETE
    5. Cannot edit is assignment.editable is false
    """

    # Setup
    assert teacher.user.assignment_set.exists() is False
    assignments[0].owner.add(teacher.user)

    # 1. Must be authenticated
    url = (
        reverse("REST:assignment-detail", args=[assignments[0].pk])
        + "?format=json"
    )

    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert login_teacher(client, teacher)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # 2. Must be owner to GET
    retrieved_assignment = json.loads(response.content)
    assert retrieved_assignment["title"] == assignments[0].title
    for q in retrieved_assignment["questions"]:
        assert q["question"]["pk"] in assignments[0].questions.values_list(
            "pk", flat=True
        )

    response = client.get(
        reverse("REST:assignment-detail", args=[assignments[1].pk])
        + "?format=json"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # 3. Must be owner to PATCH and submit question list
    response = client.patch(
        url,
        {
            "title": assignments[0].title,
            "questions": retrieved_assignment["questions"],
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.patch(
        url,
        {
            "title": assignments[0].title,
            "questions": retrieved_assignment["questions"][0:2],
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.patch(
        reverse("REST:assignment-detail", args=[assignments[1].pk]),
        {
            "title": assignments[1].title,
            "questions": retrieved_assignment["questions"],
        },
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # 4. No one can DELETE
    response = client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # 5. Cannot edit if assignment.editable is false
    with mock.patch(
        "peerinst.models.Assignment.editable", new_callable=mock.PropertyMock
    ) as mock_editable:
        mock_editable.return_value = False
        response = client.patch(
            url,
            {
                "title": assignments[0].title,
                "questions": retrieved_assignment["questions"],
            },
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.skip
def test_assignmentquestions_detail(client, assignments, questions, teacher):
    """
    See peerinst/tests/views/test_nonLTI_views.py test_assignment_update_post
    """
    pass


@pytest.mark.django_db
def test_discipline_list(client, admin, disciplines, student, teacher):
    """
    Requirements:
    1. Must be authenticated
    2. Must not be a student to GET
    3. Must be admin for anything else
    """

    # 1. Must be authenticated
    url = reverse("REST:discipline-list")

    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # 2. Must not be a student to GET
    assert login_student(client, student)

    url = reverse("REST:discipline-list")

    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert login_teacher(client, teacher)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    retrieved_disciplines = json.loads(response.content)
    for d in disciplines:
        assert d.pk in [d["pk"] for d in retrieved_disciplines]

    # 3. Must be admin for anything else
    response = client.post(url, {"title": "New discipline"}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
