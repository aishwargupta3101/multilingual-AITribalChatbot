def test_tts(client):
    payload = {
        "text": "Hello",
        "language": "English"
    }

    response = client.post(
        "/api/v1/tts",
        json=payload
    )

    assert response.status_code == 200
    assert response.content
    assert response.headers["content-type"].startswith("audio/")