def _criar_manga(client, headers):
    resposta = client.post("/mangas/", headers=headers, json={
        "titulo": "One Piece", "autor": "Eiichiro Oda",
        "genero": "Shounen", "status": "Em andamento",
    })
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_adicionar_volume(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)

    resposta = client.post(
        f"/mangas/{manga_id}/volumes",
        headers=admin_headers,
        json={"numero": 1, "comprado": False},
    )
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["numero"] == 1
    assert corpo["comprado"] is False


def test_volume_duplicado(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 1})
    resposta = client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 1})
    assert resposta.status_code == 400


def test_atualizar_volume_via_body(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 1})

    resposta = client.put(
        f"/mangas/{manga_id}/volumes/1",
        json={"comprado": True, "capa_volume": "https://img.exemplo/v1.jpg"},
    )
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["comprado"] is True
    assert corpo["capa_volume"].startswith("https://")


def test_listar_volumes(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 1})
    client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 2})

    resposta = client.get(f"/mangas/{manga_id}/volumes")
    assert resposta.status_code == 200
    assert [v["numero"] for v in resposta.json()] == [1, 2]


def test_remover_volume(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    client.post(f"/mangas/{manga_id}/volumes", headers=admin_headers, json={"numero": 1})

    resposta = client.delete(f"/mangas/{manga_id}/volumes/1")
    assert resposta.status_code == 200
    assert client.get(f"/mangas/{manga_id}/volumes").json() == []
