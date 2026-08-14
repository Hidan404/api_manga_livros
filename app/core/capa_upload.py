"""Upload de capas via Cloudinary (Sprint 5).

- Valida tamanho (máx. 5MB), content-type e extensão ANTES do upload.
- Configura o SDK a partir de ``CLOUDINARY_URL`` (formato
  ``cloudinary://<api_key>:<api_secret>@<cloud_name>``).
- Grava apenas a **URL** retornada pelo Cloudinary na coluna String do banco
  (corrige o bug de gravar bytes binários em coluna String).
"""

import io

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

from app.core.configuracao import config

TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB
CONTENT_TYPES_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}
EXTENSOES_PERMITIDAS = {"jpg", "jpeg", "png", "webp", "gif"}


def _configurar_sdk():
    """Configura o SDK do Cloudinary a partir de ``CLOUDINARY_URL``."""
    if not config.CLOUDINARY_URL:
        return False
    from urllib.parse import urlparse

    parsed = urlparse(config.CLOUDINARY_URL)
    if not parsed.hostname or not parsed.username or not parsed.password:
        return False
    cloudinary.config(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password,
        secure=True,
    )
    return True


def _validar_e_ler(arquivo: UploadFile) -> bytes:
    """Valida tipo/extensão/tamanho e lê o conteúdo do arquivo."""

    content_type = (arquivo.content_type or "").lower()
    if content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido ({content_type or 'desconhecido'}). "
                   "Use JPEG, PNG, WebP ou GIF.",
        )

    nome = arquivo.filename or ""
    extensao = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensão de arquivo não permitida ({extensao or 'sem extensão'}).",
        )

    conteudo = arquivo.file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande (máx. {TAMANHO_MAXIMO // (1024 * 1024)}MB).",
        )
    return conteudo


def fazer_upload(arquivo: UploadFile, pasta: str, public_id: str) -> str:
    """Valida e envia a imagem ao Cloudinary, retornando a URL segura."""

    # Validação do arquivo primeiro: arquivo inválido sempre retorna 400,
    # mesmo que o Cloudinary não esteja configurado.
    conteudo = _validar_e_ler(arquivo)

    if not _configurar_sdk():
        raise HTTPException(
            status_code=503,
            detail="Upload não configurado: defina CLOUDINARY_URL (variável de ambiente).",
        )

    try:
        resultado = cloudinary.uploader.upload(
            io.BytesIO(conteudo),
            folder=pasta,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
    except Exception as exc:  # cloudinary.APIError e afins
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao enviar imagem ao Cloudinary: {exc}",
        ) from exc

    url = resultado.get("secure_url")
    if not url:
        raise HTTPException(
            status_code=502,
            detail="Cloudinary não retornou uma URL para a imagem.",
        )
    return url
