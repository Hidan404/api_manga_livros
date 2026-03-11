import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    response = client.post("/auth/login", json={
        "email": "hidan@gmail.com",
        "senha": "hidan"
    })

    token = response.json()["access_token"]
    return token