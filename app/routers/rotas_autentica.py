
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.controllers.autenticar_controller import AuthController
from app.core.rate_limit import limiter
from app.database.conexao import get_db
from app.schemas.autentica_schemas import LoginSchema, RefreshTokenSchema, Token

rota = APIRouter(prefix="/auth", tags=["Autenticação"])
auth_controller = AuthController()


# Login: valida credenciais, emite access + refresh e define os cookies HttpOnly.
@rota.post("/login", response_model=Token, summary="Login de usuário",
           description="Autentica um usuário e retorna tokens (access + refresh) e cookies HttpOnly.")
@limiter.limit("10/minute")
def login(request: Request, payload: LoginSchema, response: Response, db: Session = Depends(get_db)):
    return auth_controller.login(db, payload.email, payload.senha, response)


# Refresh: lê o refresh token do cookie (Path=/auth) ou do corpo, rotaciona e
# reescreve os cookies.
@rota.post("/refresh", response_model=Token, summary="Atualizar token",
           description="Rotaciona o refresh token (cookie ou corpo) e emite um novo par.")
def refresh_token(
    request: Request,
    response: Response,
    payload: RefreshTokenSchema | None = None,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("refresh_token") or (payload.refresh_token if payload else None)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não fornecido (envie o cookie ou o corpo)",
        )
    return auth_controller.refresh_token(db, token, response)


# Logout: revoga o refresh token no banco e limpa os cookies.
@rota.post("/logout", summary="Logout",
           description="Revoga o refresh token atual e limpa os cookies de autenticação.")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    return auth_controller.logout(db, request.cookies.get("refresh_token"), response)
