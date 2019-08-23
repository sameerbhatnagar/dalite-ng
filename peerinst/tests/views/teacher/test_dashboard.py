from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


def test_student_activity__dashboard(
    client, teacher, group, student_group_assignments
):
    assert login_teacher(client, teacher)
    group.teacher.add(teacher)
    teacher.current_groups.add(group)

    resp = client.get(reverse("teacher-dashboard"))

    assert resp.status_code == 200
    assert any(
        t.name == "peerinst/teacher/cards/student_activity_card.html"
        for t in resp.templates
    )
    assert any(
        t.name == "peerinst/teacher/dashboard.html" for t in resp.templates
    )
    assert str(student_group_assignments[0].assignment.title) in resp.content
    assert str(student_group_assignments[1].assignment.title) in resp.content
