from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_adicionar_volume(auth_token):

    response = client.post(
        "/mangas/1/volumes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "numero": 1
        }
    )

    assert response.status_code == 201