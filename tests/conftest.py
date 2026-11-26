
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.auth.auth_routes import get_current_user


TEST_USER = {
    "_id": "test-user-001",
    "id": "test-user-001",
    "name": "Test User",
    "email": "test@example.com",
    "is_active": True,
}


@pytest.fixture
def client():
    async def override_get_current_user():
        return TEST_USER

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_current_user, None)
