def _criar_manga(client, headers):
    resposta = client.post("/mangas/", headers=headers, json={
        "titulo": "One Piece", "autor": "Eiichiro Oda",
        "genero": "Shounen", "status": "Em andamento",
    })
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_adicionar_favorito_manga(client, admin_headers, user_headers):
    manga_id = _criar_manga(client, admin_headers)

    resposta = client.post(f"/favoritos/manga/{manga_id}", headers=user_headers)
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["manga_id"] == manga_id
    assert corpo["titulo"] == "One Piece"


def test_favorito_duplicado(client, admin_headers, user_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/favoritos/manga/{manga_id}", headers=user_headers)
    resposta = client.post(f"/favoritos/manga/{manga_id}", headers=user_headers)
    assert resposta.status_code == 400


def test_favorito_manga_inexistente(client, user_headers):
    resposta = client.post("/favoritos/manga/9999", headers=user_headers)
    assert resposta.status_code == 404


def test_listar_favoritos_com_titulo(client, admin_headers, user_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/favoritos/manga/{manga_id}", headers=user_headers)

    resposta = client.get("/favoritos/manga/", headers=user_headers)
    assert resposta.status_code == 200
    favoritos = resposta.json()
    assert len(favoritos) == 1
    assert favoritos[0]["titulo"] == "One Piece"


def test_remover_favorito(client, admin_headers, user_headers):
    manga_id = _criar_manga(client, admin_headers)
    criado = client.post(f"/favoritos/manga/{manga_id}", headers=user_headers).json()
    favorito_id = criado["id"]

    removido = client.delete(f"/favoritos/manga/{favorito_id}", headers=user_headers)
    assert removido.status_code == 200
    assert client.get("/favoritos/manga/", headers=user_headers).json() == []


def test_deletar_manga_remove_favoritos_cascade(client, admin_headers, user_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/favoritos/manga/{manga_id}", headers=user_headers)

    client.delete(f"/mangas/{manga_id}", headers=admin_headers)
    assert client.get("/favoritos/manga/", headers=user_headers).json() == []
