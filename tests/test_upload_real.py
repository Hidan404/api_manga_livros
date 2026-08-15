"""Teste de integração com o Cloudinary (upload real).

Só roda quando `CLOUDINARY_URL` estiver definida no ambiente — no GitHub Actions
ela vem do secret do repositório. Localmente (sem a variável) o teste é pulado.
"""

import base64
import io
import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("CLOUDINARY_URL"),
    reason="CLOUDINARY_URL ausente — upload real só em CI (secret do GitHub)",
)

# JPEG 1x1 válido, mínimo que o Cloudinary aceita
_JPEG_1X1 = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AVN//2Q=="
)


def _criar_manga(client, admin_headers) -> int:
    resposta = client.post(
        "/mangas/",
        headers=admin_headers,
        json={
            "titulo": "Upload Real CI",
            "autor": "CI",
            "genero": "Teste",
            "status": "Em lancamento",
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def test_upload_capa_real_cloudinary(client, admin_headers):
    manga_id = _criar_manga(client, admin_headers)

    resposta = client.post(
        f"/mangas/{manga_id}/upload-capa",
        headers=admin_headers,
        files={"arquivo": ("capa.jpg", io.BytesIO(_JPEG_1X1), "image/jpeg")},
    )

    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["mensagem"]
    assert dados["capa_url"].startswith("https://res.cloudinary.com/")
