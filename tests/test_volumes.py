from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

"""def test_adicionar_volume(auth_token):

    # cria mangá primeiro
    manga = client.post(
        "/mangas",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "titulo": "Naruto",
            "autor": "Kishimoto"
        }
    )

    manga_id = manga.json()["id"]
    print(manga.status_code, manga.json())

    # adiciona volume
    response = client.post(
        f"/mangas/{manga_id}/volumes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "numero": 1
        }
    )

    assert response.status_code == 201"""

def test_adicionar_volume(auth_token):

    manga = client.post(
        "/mangas",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "titulo": "Naruto",
            "autor": "Kishimoto",
            "genero": "Shonen",
            "status": "Completo"
        }
    )

    assert manga.status_code == 201

    manga_id = manga.json()["id"]

    response = client.post(
        f"/mangas/{manga_id}/volumes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"numero": 1}
    )

    assert response.status_code == 201