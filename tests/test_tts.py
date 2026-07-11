from tests.conftest import client
def test_tts():
    payload ={
        "text":"Hello",
        "language":"English"
    }
    response = client.post(
        "/api/v1/tts/",
        json=payload
    )
    assert response.status_code == 200
    assert response.json()["success"] is True