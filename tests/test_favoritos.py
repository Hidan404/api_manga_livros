import requests

BASE_URL = "http://127.0.0.1:8000"


def test_add_favorito_manga(headers):
    r = requests.post(
        f"{BASE_URL}/favoritos/manga/1",
        headers=headers
    )

    assert r.status_code in (200, 201)
