from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_adicionar_favorito(auth_token):

    response = client.post(
        "/favoritos/manga/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code in [200, 201]