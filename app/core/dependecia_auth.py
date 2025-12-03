from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.utils.jwt_gerenciador import Autenticacao_config

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")
jwt_manager = Autenticacao_config()


def get_current_user(token: str = Depends(oauth2)):
    payload = jwt_manager.decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    return {"id": int(payload["sub"])}


def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        from app.database.conexao import SessionLocal
        from app.models.usuario_model import Usuario

        db = SessionLocal()
        usuario = db.query(Usuario).filter(Usuario.id == user["id"]).first()
        db.close()

        if usuario is None or usuario.role != role:
            raise HTTPException(
                status_code=403,
                detail="Acesso negado"
            )
        return usuario
    return role_checker
