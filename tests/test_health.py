def test_health(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert "mongodb" in data
    assert "llama" in data