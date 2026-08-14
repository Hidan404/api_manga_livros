"""Gerenciamento de tokens JWT (Sprint 2).

Correções aplicadas nesta sprint:
- `create_refresh_token` era definido DUAS vezes (a 2ª sobrescrevia a 1ª e usava
  `config.ALGORITHM`/`expirar_em` inexistentes) → refresh nunca funcionava.
- `expirar_em` → `expirar_na` (nome correto do método).
- Access e refresh usam CHAVES diferentes (`SECRET_KEY` vs `REFRESH_SECRET_KEY`).
- `ALGORITHM` agora vem de `config.ALGORITHM` (Sprint 1).
- `decode_token` aceita o segredo por parâmetro para decodificar refresh tokens.
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.configuracao import config


class Autenticacao_config:
    def __init__(self):
        self.ALGORITMO = config.ALGORITHM
        self.SECRET = config.SECRET_KEY
        self.REFRESH_SECRET = config.REFRESH_SECRET_KEY

    def utc_now(self) -> datetime:
        return datetime.now(UTC)

    def expirar_na(self, minutos: int | None = None, dias: int | None = None) -> datetime:
        """Retorna datetime de expiração com base em minutos OU dias."""
        if minutos is not None:
            return self.utc_now() + timedelta(minutes=minutos)
        if dias is not None:
            return self.utc_now() + timedelta(days=dias)
        return self.utc_now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    def base_payload(self, user_id: int | str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {"sub": str(user_id)}
        if extra:
            payload.update(extra)
        return payload

    def create_access_token(self, user_id: int | str, expires_minutes: int | None = None, role: str | None = None) -> str:
        """Gera um JWT do tipo 'access' assinado com SECRET_KEY."""
        expire = self.expirar_na(minutos=expires_minutes or config.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = self.base_payload(user_id, {"type": "access", "exp": int(expire.timestamp())})
        if role:
            payload["role"] = role
        return jwt.encode(payload, self.SECRET, algorithm=self.ALGORITMO)

    def create_refresh_token(self, user_id: int | str, expires_days: int | None = None) -> str:
        """Gera um JWT do tipo 'refresh' assinado com REFRESH_SECRET_KEY.

        Inclui um 'jti' (id único) que é persistido na tabela `refresh_tokens`
        para permitir revogação e detecção de reuso (rotação).
        """
        expire = self.expirar_na(dias=expires_days or config.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = secrets.token_hex(16)
        payload = self.base_payload(user_id, {
            "type": "refresh",
            "exp": int(expire.timestamp()),
            "jti": jti,
        })
        return jwt.encode(payload, self.REFRESH_SECRET, algorithm=self.ALGORITMO)

    def decode_token(self, token: str, secret: str | None = None) -> dict[str, Any]:
        """Decodifica e valida um JWT. Levanta JWTError se inválido/expirado."""
        secret = secret or self.SECRET
        return jwt.decode(token, secret, algorithms=[self.ALGORITMO])

    def decode_access_token(self, token: str) -> dict[str, Any]:
        return self.decode_token(token, self.SECRET)

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        return self.decode_token(token, self.REFRESH_SECRET)

    def is_token_type(self, payload: dict[str, Any], expected: str) -> bool:
        """Verifica se o 'type' do payload bate com 'access' ou 'refresh'."""
        return str(payload.get("type", "")).lower() == expected.lower()

    @staticmethod
    def get_user_id_from_payload(payload: dict[str, Any]) -> int | None:
        sub = payload.get("sub")
        try:
            return int(sub)
        except Exception:
            return None

    def verificar_refresh_token(self, token: str) -> dict[str, Any] | None:
        """Valida o refresh token (chave + tipo). Retorna o payload ou None."""
        try:
            payload = self.decode_refresh_token(token)
            if not self.is_token_type(payload, "refresh"):
                raise JWTError("Token inválido para refresh")
            return payload
        except JWTError:
            return None
