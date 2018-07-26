def login_user(client, user):
    res = client.login(username=user.username, password="test")
    assert res
