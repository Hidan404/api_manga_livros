def _livro_payload(titulo="Clean Code"):
    return {
        "titulo": titulo,
        "autor": "Robert Martin",
        "genero": "Programação",
        "isbn": "978-0132350884",
        "ano": 2008,
        "sinopse": "Princípios de código limpo.",
    }


def test_user_nao_cria_livro(client, user_headers):
    resposta = client.post("/livros/", headers=user_headers, json=_livro_payload())
    assert resposta.status_code == 403


def test_admin_cria_livro_com_isbn_e_sinopse(client, admin_headers):
    resposta = client.post("/livros/", headers=admin_headers, json=_livro_payload())
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["isbn"] == "978-0132350884"
    assert corpo["sinopse"] == "Princípios de código limpo."


def test_listar_livros(client, admin_headers):
    client.post("/livros/", headers=admin_headers, json=_livro_payload())
    resposta = client.get("/livros/")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_atualizar_livro(client, admin_headers):
    criado = client.post("/livros/", headers=admin_headers, json=_livro_payload())
    livro_id = criado.json()["id"]

    resposta = client.put(
        f"/livros/{livro_id}",
        headers=admin_headers,
        json={"ano": 2018},
    )
    assert resposta.status_code == 200
    assert resposta.json()["ano"] == 2018


def test_deletar_livro(client, admin_headers):
    criado = client.post("/livros/", headers=admin_headers, json=_livro_payload())
    livro_id = criado.json()["id"]

    assert client.delete(f"/livros/{livro_id}", headers=admin_headers).status_code == 200
    assert client.get(f"/livros/{livro_id}").status_code == 404
