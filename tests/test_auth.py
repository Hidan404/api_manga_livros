from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)


def test_register():
    email = f"teste{uuid.uuid4()}@email.com"
    response = client.post("/auth/register", json={
        "nome": "Teste",
        "email": email,
        "senha": "123456"
    })

    assert response.status_code in [200, 201]


def test_login():

    email = f"teste{uuid.uuid4()}@email.com"

    # cria usuário primeiro
    client.post("/auth/register", json={
        "nome": "Teste",
        "email": email,
        "senha": "123456"
    })

    # agora faz login
    response = client.post("/auth/login", json={
        "email": email,
        "senha": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()