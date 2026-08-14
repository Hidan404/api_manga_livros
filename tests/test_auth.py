import uuid


def _novo_usuario(client):
    email = f"auth-{uuid.uuid4().hex[:8]}@teste.com"
    resposta = client.post("/auth/register", json={
        "nome": "Teste Auth", "email": email, "senha": "123456",
    })
    assert resposta.status_code == 200, resposta.text
    return email


def test_register(client):
    email = f"register-{uuid.uuid4().hex[:8]}@teste.com"
    resposta = client.post("/auth/register", json={
        "nome": "Novo", "email": email, "senha": "123456",
    })
    assert resposta.status_code == 200
    assert resposta.json()["msg"] == "Usuário criado com sucesso"


def test_register_email_duplicado(client):
    email = _novo_usuario(client)
    resposta = client.post("/auth/register", json={
        "nome": "Outro", "email": email, "senha": "123456",
    })
    assert resposta.status_code == 400


def test_login_retorna_tokens_e_cookies(client):
    email = _novo_usuario(client)
    resposta = client.post("/auth/login", json={"email": email, "senha": "123456"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "access_token" in corpo
    assert "refresh_token" in corpo
    assert corpo["role"] == "user"
    nomes_cookies = [c.name for c in client.cookies.jar]
    assert "access_token" in nomes_cookies
    assert "refresh_token" in nomes_cookies


def test_login_senha_errada(client):
    email = _novo_usuario(client)
    resposta = client.post("/auth/login", json={"email": email, "senha": "errada"})
    assert resposta.status_code == 401


def test_rota_protegida_via_cookie(client):
    email = _novo_usuario(client)
    client.post("/auth/login", json={"email": email, "senha": "123456"})
    # sem header Authorization — o cookie access_token autentica
    resposta = client.get("/mangas/")
    assert resposta.status_code == 200


def test_refresh_rotaciona_e_reuso_e_rejeitado(client):
    email = _novo_usuario(client)
    login = client.post("/auth/login", json={"email": email, "senha": "123456"})
    refresh_antigo = login.json()["refresh_token"]

    # rotaciona via cookie (TestClient envia o refresh cookie em /auth/refresh)
    rotacao = client.post("/auth/refresh")
    assert rotacao.status_code == 200, rotacao.text

    # reuso do refresh antigo (sem cookie ativo, como um atacante) → 401
    client.cookies.clear()
    reuso = client.post("/auth/refresh", json={"refresh_token": refresh_antigo})
    assert reuso.status_code == 401
    assert "Sessão comprometida" in reuso.json()["detail"]


def test_logout_limpa_cookies_e_revoga(client):
    email = _novo_usuario(client)
    client.post("/auth/login", json={"email": email, "senha": "123456"})
    assert len([c for c in client.cookies.jar]) >= 2

    saida = client.post("/auth/logout")
    assert saida.status_code == 200
    assert len([c for c in client.cookies.jar]) == 0


def test_somente_admin_cria_manga(client, user_headers, admin_headers):
    manga = {"titulo": "X", "autor": "Y", "genero": "Z", "status": "S"}
    negado = client.post("/mangas/", headers=user_headers, json=manga)
    assert negado.status_code == 403
    permitido = client.post("/mangas/", headers=admin_headers, json=manga)
    assert permitido.status_code == 201
