def _manga_payload(titulo="Naruto"):
    return {
        "titulo": titulo,
        "autor": "Masashi Kishimoto",
        "artista": "Kishimoto",
        "genero": "Shounen",
        "status": "Completo",
        "sinopse": "Um ninja.",
        "data_lancamento": "1999-09-21",
        "capa_url": "https://img.exemplo/naruto.jpg",
    }


def test_user_nao_cria_manga(client, user_headers):
    resposta = client.post("/mangas/", headers=user_headers, json=_manga_payload())
    assert resposta.status_code == 403


def test_admin_cria_manga_completo(client, admin_headers):
    resposta = client.post("/mangas/", headers=admin_headers, json=_manga_payload())
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["artista"] == "Kishimoto"
    assert corpo["data_lancamento"] == "1999-09-21"
    assert corpo["capa_url"].startswith("https://")


def test_listar_e_obter_manga(client, admin_headers):
    criado = client.post("/mangas/", headers=admin_headers, json=_manga_payload())
    manga_id = criado.json()["id"]

    lista = client.get("/mangas/")
    assert lista.status_code == 200
    assert any(m["id"] == manga_id for m in lista.json())

    detalhe = client.get(f"/mangas/{manga_id}")
    assert detalhe.status_code == 200
    assert detalhe.json()["titulo"] == "Naruto"


def test_atualizar_manga_com_sinopse(client, admin_headers):
    criado = client.post("/mangas/", headers=admin_headers, json=_manga_payload())
    manga_id = criado.json()["id"]

    resposta = client.put(
        f"/mangas/{manga_id}",
        headers=admin_headers,
        json={"sinopse": "Sinopse nova", "status": "Em andamento"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["sinopse"] == "Sinopse nova"
    assert resposta.json()["status"] == "Em andamento"


def test_deletar_manga(client, admin_headers):
    criado = client.post("/mangas/", headers=admin_headers, json=_manga_payload())
    manga_id = criado.json()["id"]

    removido = client.delete(f"/mangas/{manga_id}", headers=admin_headers)
    assert removido.status_code == 200

    inexistente = client.get(f"/mangas/{manga_id}")
    assert inexistente.status_code == 404
