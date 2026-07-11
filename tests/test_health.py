from tests.conftest import client
def test_health():
    response = client.get("/api/v1/health/")
    assert response.status_code ==200
    data = response.json()
    assert "backend"in data
    assert "mongodb" in data
    assert "llama" in data