from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_criar_livro(auth_token):

    response = client.post(
        "/livros/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "titulo": "Clean Code",
            "autor": "Robert Martin",
            "genero": "Programação",
        }
    )

    assert response.status_code == 201