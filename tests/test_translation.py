def test_translation(client):
    payload = {
        "text": "Hello",
        "source_language": "English",
        "target_language": "Hindi"
    }

    response = client.post(
        "/api/v1/translation/",
        json=payload
    )

    assert response.status_code == 200
    assert response.json()["success"] is True