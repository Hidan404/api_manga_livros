"""Dependências de autenticação e autorização (Sprint 2).

ÚNICA fonte de autenticação da aplicação (antes havia duplicata em
`utils/dependecias_utils.py`, que foi removida).

Mudanças:
- `get_current_user` aceita o token do header `Authorization: Bearer` OU do
  cookie HttpOnly `access_token` (transição para cookies, ver PLANO seção 5).
- Valida `token_type=access` (rejeita refresh token usado como access).
- A role é lida do BANCO (não derivada de e-mail como antes).
- `require_role` / `require_any_role` usam o registro central `roles.py`.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.roles import ROLES_VALIDAS, RoleUsuario
from app.database.conexao import SessionLocal
from app.models.usuario_model import Usuario
from app.utils.jwt_gerenciador import Autenticacao_config

# auto_error=False: permite cair no fallback do cookie quando não houver header
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

jwt_manager = Autenticacao_config()


def get_current_user(request: Request, token: str = Depends(oauth2)):
    """Retorna o usuário autenticado a partir do header Bearer ou do cookie."""
    if not token:
        # Fallback: cookie HttpOnly 'access_token' (entrega via cookies)
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Envie o token no header ou no cookie.",
        )

    try:
        payload = jwt_manager.decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        ) from None

    if not jwt_manager.is_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não é do tipo access",
        )

    user_id = jwt_manager.get_user_id_from_payload(payload)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuário inválido no token",
        )

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
    finally:
        db.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,  # role vinda do banco
    }


def _normalizar_role(role) -> str:
    """Aceita string ('admin') ou membro do enum (RoleUsuario.ADMIN)."""
    return role.value if isinstance(role, RoleUsuario) else role


def require_role(role):
    """Exige uma role específica. Ex.: require_role(RoleUsuario.ADMIN)."""
    expected = _normalizar_role(role)

    if expected not in ROLES_VALIDAS:
        raise ValueError(f"Role '{expected}' não existe no registro de roles")

    def role_checker(user=Depends(get_current_user)):
        if user["role"] != expected:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado",
            )
        return user

    return role_checker


def require_any_role(*roles):
    """Exige UMA das roles informadas. Ex.: require_any_role("admin", "editor")."""
    allowed = {_normalizar_role(r) for r in roles}

    if not allowed <= ROLES_VALIDAS:
        raise ValueError(f"Roles {allowed} contém valores fora do registro de roles")

    def role_checker(user=Depends(get_current_user)):
        if user["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado",
            )
        return user

    return role_checker
