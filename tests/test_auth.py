from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register():
    response = client.post("/auth/register", json={
        "nome": "Teste",
        "email": "teste@email.com",
        "senha": "123456"
    })

    assert response.status_code in [200, 201]


def test_login():
    response = client.post("/auth/login", json={
        "email": "teste@email.com",
        "senha": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()