from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_criar_manga(auth_token):

    response = client.post(
        "/mangas/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "titulo": "Naruto",
            "autor": "Masashi Kishimoto",
            "genero": "Shounen",
            "status": "Completo"
        }
    )

    assert response.status_code == 201


def test_listar_mangas(auth_token):

    response = client.get(
        "/mangas/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200