from tests.conftest import client
def test_speech():
    payload ={
        "language":"English"
    }
    response = client.post(
        "/api/v1/speech/",
        json=payload
    )
    assert response.status_code ==200
    assert response.json()["success"] is True