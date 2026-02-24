import requests

BASE_URL = "http://127.0.0.1:8000"


def test_login_ok():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "ronaldkurouzo@gmail.com",
            "senha": "hidan"
        }
    )

    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_errado():
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "ronaldkurouzo@gmail.com",
            "senha": "senha_errada"
        }
    )

    assert r.status_code in (400, 401)
