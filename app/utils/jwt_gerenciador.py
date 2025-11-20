from datetime import datetime, UTC, timedelta
from typing import Optional, Dict, Any
import secrets
from jose import jwt, JWTError
from app.core.configuracao import config


class Autenticacao_config():
    def __init__(self):
        self.ALGORITMO = "HS256"
        self.SECRET = config.SECRET_KEY

    def utc_now(self) ->datetime:
        return datetime.now(UTC)
    
    def expirar_na(self,minutos: Optional[int] = None, dias: Optional[int] = None) ->datetime:
        if minutos is not None:
            return self.utc_now() + timedelta(minutos=minutos)
        if dias is not None:
            return self.utc_now() + timedelta(dias=dias)
        
        return self.utc_now() + timedelta(minutes=60)
    
    def base_payload(self, user_id: int | str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"sub": str(user_id)}
        if extra:
            payload.update(extra)
        return payload
    
    def create_access_token(self, user_id: int | str, expires_minutes: Optional[int] = None, role: Optional[str] = None) -> str:
        """
        Gera um JWT do tipo 'access'.
        - user_id: id do usuário (colocar em sub)
        - expires_minutes: sobrescreve a duração padrão (em minutos)
        - role: se quiser incluir role no payload
        """
        expire = self.expirar_na(minutes=expires_minutes or config.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = self.base_payload(user_id, {"type": "access", "exp": int(expire.timestamp())})
        if role:
            payload["role"] = role
        token = jwt.encode(payload, self.SECRET, algorithm=self.ALGORITMO)

        return token
    
    def create_refresh_token(self, user_id: int | str, expires_days: Optional[int] = None) -> str:
        """
        Gera um JWT do tipo 'refresh' com um 'jti' (id único).
        Salvamos o JWT ou o jti no banco para poder revogar.
        """
        expire = self.expirar_na(days=expires_days or config.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = secrets.token_hex(16)  # identificador único do token
        payload = self.base_payload(user_id, {"type": "refresh", "exp": int(expire.timestamp()), "jti": jti})
        token = jwt.encode(payload, self.SECRET, algorithm=self.ALGORITMO)
        return token

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica um token JWT e retorna o payload.
        Levanta JWTError se inválido/expirado.
        """
        try:
            payload = jwt.decode(token, self.SECRET, algorithms=[self.ALGORITMO])
            return payload
        except JWTError as e:
            # Lançar nocvamente para o caller tratar (HTTPException, log, etc.)
            raise

    def is_token_type(self, payload: Dict[str, Any], expected: str) -> bool:
        """
        Verifica se 'type' do payload bate com 'access' ou 'refresh'
        """
        return str(payload.get("type", "")).lower() == expected.lower()

    # Uso auxiliar: extrair user_id (sub) com segurança
    @staticmethod
    def get_user_id_from_payload(payload: Dict[str, Any]) -> Optional[int]:
        sub = payload.get("sub")
        try:
            return int(sub)
        except Exception:
            return None