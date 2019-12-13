import uuid


def test_oauth_signature(client, settings):
    settings.LTI_CLIENT_KEY = str(uuid.uuid1())
    settings.LTI_CLIENT_SECRET = str(uuid.uuid1())

    response = client.post(
        "/lti/",
        {
            "oauth_timestamp": uuid.uuid1().int,
            "oauth_nonce": uuid.uuid1(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_signature": str(uuid.uuid1()),
        },
    )

    print(response)

    assert response.status == 200
