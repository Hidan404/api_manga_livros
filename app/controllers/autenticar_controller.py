"""Controller de autenticação (Sprint 2).

Fluxos:
- login: valida credenciais, emite access + refresh, persiste o refresh (jti)
  na tabela `refresh_tokens` e define os cookies HttpOnly.
- refresh: ROTAÇÃO — valida o refresh, revoga o jti usado, emite um novo par.
  Se um jti já revogado for reutilizado → possível roubo → revoga a sessão inteira.
- logout: revoga o refresh e limpa os cookies.

Cookies (PLANO seção 5):
- access_token: HttpOnly + Secure + SameSite(Lax), Path=/, 15 min
- refresh_token: HttpOnly + Secure + SameSite(Strict), Path=/auth, 30 dias
"""

from datetime import UTC, datetime

from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.configuracao import config
from app.models.refresh_token_model import RefreshToken
from app.models.usuario_model import Usuario
from app.utils.jwt_gerenciador import Autenticacao_config
from app.utils.senha_hasher import SenhaHasher

jwt = Autenticacao_config()


class AuthController:

    # ----------------------- helpers de cookie -----------------------

    def _definir_cookies(self, response: Response, access_token: str, refresh_token: str):
        """Define access e refresh em cookies HttpOnly."""
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=config.COOKIE_SECURE,
            samesite=config.COOKIE_SAMESITE,
            max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            domain=config.COOKIE_DOMAIN or None,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=config.COOKIE_SECURE,
            samesite="strict",  # nunca enviado em requests cross-site
            max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/auth",  # só é enviado às rotas /auth (refresh/logout)
            domain=config.COOKIE_DOMAIN or None,
        )

    def _limpar_cookies(self, response: Response):
        response.delete_cookie("access_token", path="/", domain=config.COOKIE_DOMAIN or None)
        response.delete_cookie("refresh_token", path="/auth", domain=config.COOKIE_DOMAIN or None)

    # ----------------------- helpers de banco -----------------------

    def _persistir_refresh(self, db: Session, usuario_id: int, jti: str, expira_em: datetime):
        db.add(RefreshToken(usuario_id=usuario_id, jti=jti, expira_em=expira_em))
        db.commit()

    def _revogar_todos(self, db: Session, usuario_id: int):
        """Invalida todos os refresh tokens do usuário (sessão comprometida)."""
        db.query(RefreshToken).filter(RefreshToken.usuario_id == usuario_id).update(
            {RefreshToken.revogado: True}
        )
        db.commit()

    # ----------------------- fluxos -----------------------

    def login(self, db: Session, email: str, senha: str, response: Response):
        usuario = db.query(Usuario).filter(Usuario.email == email).first()

        if not usuario or not SenhaHasher.verificar_senha(senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
            )

        access = jwt.create_access_token(user_id=usuario.id, role=usuario.role)
        refresh = jwt.create_refresh_token(user_id=usuario.id)

        payload_refresh = jwt.verificar_refresh_token(refresh)
        expira_em = datetime.fromtimestamp(payload_refresh["exp"], tz=UTC)
        self._persistir_refresh(db, usuario.id, payload_refresh["jti"], expira_em)
        self._definir_cookies(response, access, refresh)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "role": usuario.role,
        }

    def refresh_token(self, db: Session, refresh_token: str, response: Response):
        payload = jwt.verificar_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
            )

        jti = payload["jti"]
        user_id = int(payload["sub"])

        stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

        # Reuso de token já revogado/rotacionado = sinal de roubo
        if not stored or stored.revogado:
            if stored:
                self._revogar_todos(db, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sessão comprometida. Faça login novamente.",
            )

        # expira_em pode vir naive em alguns dialetos (ex.: SQLite nos testes);
        # normaliza para tz-aware antes de comparar com UTC.
        expira_em = stored.expira_em
        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(tzinfo=UTC)
        if expira_em < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado",
            )

        # ROTAÇÃO: revoga o token atual antes de emitir o novo par
        stored.revogado = True
        db.commit()

        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )

        access = jwt.create_access_token(user_id=usuario.id, role=usuario.role)
        refresh = jwt.create_refresh_token(user_id=usuario.id)

        payload_novo = jwt.verificar_refresh_token(refresh)
        expira_em = datetime.fromtimestamp(payload_novo["exp"], tz=UTC)
        self._persistir_refresh(db, usuario.id, payload_novo["jti"], expira_em)
        self._definir_cookies(response, access, refresh)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "role": usuario.role,
        }

    def logout(self, db: Session, refresh_token: str, response: Response):
        if refresh_token:
            payload = jwt.verificar_refresh_token(refresh_token)
            if payload:
                db.query(RefreshToken).filter(RefreshToken.jti == payload["jti"]).delete()
                db.commit()
        self._limpar_cookies(response)
        return {"msg": "Logout realizado com sucesso"}
