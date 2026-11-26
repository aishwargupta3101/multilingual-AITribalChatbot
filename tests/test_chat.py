
def test_chat(client):
    payload = {
        "session_id": "123",
        "question": "hello",
        "language": "English"
    }

    response = client.post(
        "/api/v1/chat/",
        json=payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
