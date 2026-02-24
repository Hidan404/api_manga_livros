import requests

BASE_URL = "http://127.0.0.1:8000"


def test_criar_manga(headers):
    r = requests.post(
        f"{BASE_URL}/mangas/",
        headers=headers,
        json={
            "titulo": "Naruto Teste",
            "autor": "Kishimoto",
            "genero": "Shounen",
            "status": "Completo",
            "sinopse": "Teste pytest",
            "capa_url": "http://img.com"
        }
    )

    assert r.status_code == 200
    assert r.json()["titulo"] == "Naruto Teste"


def test_listar_mangas():
    r = requests.get(f"{BASE_URL}/mangas/")
    assert r.status_code == 200


def test_criar_sem_token():
    r = requests.post(
        f"{BASE_URL}/mangas/",
        json={
            "titulo": "Sem token",
            "autor": "X",
            "genero": "X",
            "status": "X",
            "sinopse": "X",
            "capa_url": "X"
        }
    )

    assert r.status_code == 401
