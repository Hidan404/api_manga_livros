from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_adicionar_favorito(auth_token):

    manga = client.post(
        "/mangas/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "titulo": "One Piece",
            "autor": "Eiichiro Oda",
            "genero": "Shounen",
            "status": "Em andamento"
        }
    )
    manga_id = manga.json()["id"]
    response = client.post(
        f"/favoritos/manga/{manga_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code in [200, 201]