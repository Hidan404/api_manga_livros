import io

from app.core import capa_upload


def _criar_manga(client, headers):
    resposta = client.post("/mangas/", headers=headers, json={
        "titulo": "Manga Upload", "autor": "A", "genero": "G", "status": "S",
    })
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_upload_requer_admin(client, user_headers):
    resposta = client.post(
        "/mangas/9999/upload-capa",
        headers=user_headers,
        files={"arquivo": ("capa.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert resposta.status_code == 403


def test_upload_tipo_invalido_400(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    resposta = client.post(
        f"/mangas/{manga_id}/upload-capa",
        headers=admin_headers,
        files={"arquivo": ("capa.txt", io.BytesIO(b"nao e imagem"), "text/plain")},
    )
    assert resposta.status_code == 400
    assert "não permitido" in resposta.json()["detail"]


def test_upload_extensao_invalida_400(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)
    resposta = client.post(
        f"/mangas/{manga_id}/upload-capa",
        headers=admin_headers,
        files={"arquivo": ("capa.exe", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert resposta.status_code == 400
    assert "Extensão" in resposta.json()["detail"]


def test_upload_sem_cloudinary_503(client, admin_headers, monkeypatch):
    # Simula ambiente SEM CLOUDINARY_URL, independente do valor real
    # (localmente vazio; na CI vem o secret). Força o caminho "não configurado".
    monkeypatch.setattr(capa_upload, "_configurar_sdk", lambda: False)
    manga_id = _criar_manga(client, admin_headers)
    resposta = client.post(
        f"/mangas/{manga_id}/upload-capa",
        headers=admin_headers,
        files={"arquivo": ("capa.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert resposta.status_code == 503
    assert "CLOUDINARY_URL" in resposta.json()["detail"]
