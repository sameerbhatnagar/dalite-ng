import re

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse

from peerinst.tests.fixtures import *  # noqa
from peerinst.tests.fixtures.teacher import login_teacher


def test_dashboard__post(client, teacher):
    login_teacher(client, teacher)
    user = User.objects.create_user(
        username="test", password="test", email="test@test.com"
    )
    user.is_active = False
    user.save()
    teacher.user.is_superuser = True
    teacher.user.save()

    data = {"user": user.pk}
    resp = client.post(reverse("dashboard"), data)
    assert resp.status_code == 200

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Please verify your myDalite account"
    link = re.search(r"(http://.+)\s", mail.outbox[0].body).group(1)

    resp = client.get(link)
    assert resp.status_code == 200
    assert resp.template_name == "registration/password_reset_confirm.html"
