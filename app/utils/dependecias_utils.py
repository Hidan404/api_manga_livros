from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.utils.jwt_gerenciador import Autenticacao_config
from app.database.conexao import sessao_local as SessionLocal
from app.models.usuario_model import Usuario

# URL fictícia só para FastAPI entender o fluxo depois sera uma url real
# URL de obtenção do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

jwtm = Autenticacao_config()


def verify_token(token: str):
    """
    Decodifica e valida o JWT.
    Retorna o payload se estiver tudo ok.
    """
    try:
        payload = jwtm.decode_token(token)
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retorna o usuário autenticado baseado no token JWT.
    """
    payload = verify_token(token)

    if not jwtm.is_token_type(payload, "access"):
        raise HTTPException(status_code=401, detail="Token não é do tipo access")

    user_id = jwtm.get_user_id_from_payload(payload)

    if not user_id:
        raise HTTPException(status_code=401, detail="ID de usuário inválido no token")

    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {
        "id": user.id,
        "email": user.email,
        "role": "admin" if user.email.endswith("@admin.com") else "user"
    }


def require_role(required_role: str):
    """
    Cria uma verificação dinâmica de permissão.
    Exemplo: require_role("admin")
    """

    def role_dependency(usuario=Depends(get_current_user)):
        role = usuario.get("role")

        if role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado. Requer permissão: {required_role}",
            )

        return usuario

    return role_dependency

