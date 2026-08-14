"""Configuração central da aplicação (Sprint 1).

Usa `pydantic-settings` para ler variáveis de ambiente (e o arquivo `.env`),
substituindo a implementação anterior que misturava `os.getenv` com defaults fracos.

Lógica e mudanças:
- As variáveis são lidas automaticamente do ambiente e do `.env`
  (``SettingsConfigDict(env_file=".env")``) — não há mais `load_dotenv()` manual
  em `configuracao.py` nem em `conexao.py`.
- `ALGORITHM` passou a existir de verdade (antes estava no `.env` mas nunca era lido).
- `ENVIRONMENT` distingue desenvolvimento de produção.
- `SSL_MODE` controla o sslmode da conexão (Supabase exige `require`; local não).
- Secrets **não têm default fraco**: em `production`, a ausência derruba a aplicação
  no boot; em `development`, são aplicados valores de desenvolvimento bem identificados.
"""

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    """Configurações carregadas de variáveis de ambiente / `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---------------- Ambiente ----------------
    ENVIRONMENT: Literal["development", "production"] = "development"

    # ---------------- Banco de dados ----------------
    DATABASE_URL: str
    # sslmode: disable (local, sem SSL) | require (Supabase) | prefer | allow
    SSL_MODE: Literal["disable", "require", "prefer", "allow"] = "disable"

    # ---------------- JWT ----------------
    SECRET_KEY: str = ""
    REFRESH_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 dias (fallback em minutos)

    # ---------------- Cookies (entrega de token ao frontend — Sprint 2) ----------------
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str = ""

    # ---------------- Cloudinary (upload de capas — Sprint 5) ----------------
    CLOUDINARY_URL: str = ""

    @model_validator(mode="after")
    def _validar_secrets(self) -> "Configuracao":
        """Falha rápido em produção com secret ausente; usa valor de dev se vazio."""
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY ausente ou muito curta em produção (mínimo 32 caracteres). "
                    "Defina via variável de ambiente no Render."
                )
            if not self.REFRESH_SECRET_KEY or len(self.REFRESH_SECRET_KEY) < 32:
                raise ValueError(
                    "REFRESH_SECRET_KEY ausente ou muito curta em produção (mínimo 32 caracteres). "
                    "Defina via variável de ambiente no Render."
                )
        else:
            self.SECRET_KEY = self.SECRET_KEY or "dev-secret-key-nao-usar-em-producao"
            self.REFRESH_SECRET_KEY = self.REFRESH_SECRET_KEY or "dev-refresh-secret-nao-usar-em-producao"
        return self


config = Configuracao()