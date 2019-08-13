import json

from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


def test_messages(client, teacher, thread):
    assert login_teacher(client, teacher)

    replies = thread.replies.order_by("-created").all()
    teacher.last_page_access = replies[len(replies) // 2].created
    teacher.save()

    resp = client.post(reverse("teacher-page--messages"))
    assert resp.status_code == 200
    data = json.loads(resp.content)["threads"]

    assert len(data) == 1
    for thread in data:
        assert "id" in thread
        assert "last_reply" in thread
        assert "author" in thread["last_reply"]
        assert "content" in thread["last_reply"]
        assert thread["n_new"] == len(replies) // 2

        resp = client.get(thread["link"])
        assert resp.status_code == 200
        assert "pinax/forums/thread.html" in resp.template_name
