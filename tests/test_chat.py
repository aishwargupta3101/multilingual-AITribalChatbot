from tests.conftest import client
def test_chat():
    payload ={
        "session_id":"123",
        "question":"hello",
        "language" : "English"
    }
    response = client.post(
        "/api/v1/chat/",
        json=payload
    )
    assert response.status_code ==200
    data = response.json()
    assert data["success"] is True