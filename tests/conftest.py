import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "ronaldkurouzo@gmail.com"
SENHA = "hidan"


@pytest.fixture(scope="session")
def token():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "senha": SENHA}
    )

    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
