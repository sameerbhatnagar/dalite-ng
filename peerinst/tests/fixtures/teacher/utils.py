# -*- coding: utf-8 -*-


def login_teacher(client, teacher):
    return client.login(username=teacher.user.username, password="test")
