import json
import pytest

from django.urls import reverse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


@pytest.mark.django_db
def test_assignment_detail(client, assignment, questions, teacher):

    url = (
        reverse("REST:assignment-detail", args=[assignment.pk])
        + "?format=json"
    )

    response = client.get(url)
    assert response.status_code == 403

    assert login_teacher(client, teacher)

    response = client.get(url)
    retrieved_assignment = json.loads(response.content)

    assert retrieved_assignment["title"] == assignment.title
    for q in retrieved_assignment["questions"]:
        assert q["question"]["pk"] in assignment.questions.values_list(
            "pk", flat=True
        )
