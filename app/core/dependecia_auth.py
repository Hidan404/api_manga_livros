from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.utils.jwt_gerenciador import Autenticacao_config
from app.models.usuario_model import Usuario


bearer_scheme = HTTPBearer()
jwt_gerenciador = Autenticacao_config()


def obter_usuario_logado(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt_gerenciador =(token.credentials)

        # Verifica o tipo do token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido para acesso"
            )

        user_id = int(payload.get("sub"))
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        return usuario

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def require_role(role: str):
    """
    Dependência dinâmica para verificar roles
    Exemplo: Depends(require_role("admin"))
    """
    def role_checker(
        usuario_logado: Usuario = Depends(obter_usuario_logado)
    ):
        if usuario_logado.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Necessário papel '{role}'."
            )
        return usuario_logado

    return role_checker
