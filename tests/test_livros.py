import requests

BASE_URL = "http://127.0.0.1:8000"


def test_criar_livro(headers):
    r = requests.post(
        f"{BASE_URL}/livros/",
        headers=headers,
        json={
            "titulo": "Livro Pytest",
            "autor": "Autor",
            "genero": "Teste",
            "ano": 2024,
            "descricao": "teste"
        }
    )

    assert r.status_code == 200
    assert r.json()["titulo"] == "Livro Pytest"


def test_listar_livros():
    r = requests.get(f"{BASE_URL}/livros/")
    assert r.status_code == 200
