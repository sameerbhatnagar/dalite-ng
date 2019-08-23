from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


def test_new_questions(client, teacher, questions, assignment, disciplines):
    assert login_teacher(client, teacher)

    for question in questions[: len(questions) // 2]:
        question.discipline = disciplines[0]
        question.save()
    for question in questions[len(questions) // 2 :]:
        question.discipline = disciplines[1]
        question.save()

    teacher.disciplines.add(disciplines[0])

    resp = client.get(reverse("teacher-dashboard--new-questions"))

    assert resp.status_code == 200
    assert any(
        t.name == "peerinst/question/cards/question_card.html"
        for t in resp.templates
    )
    assert str(disciplines[0]) in resp.content
    assert str(disciplines[1]) not in resp.content

    # TODO: Add tests to validate choose_questions logic
    # E.g. no questions from teacher assignments, no favourites etc.
