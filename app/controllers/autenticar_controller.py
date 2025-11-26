from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.controllers.usuario_controller import UsuarioController
from app.utils.senha_hasher import SenhaHasher
from app.utils.jwt_gerenciador import Autenticacao_config

usuario_service = UsuarioController()
jwt = Autenticacao_config()

class AuthController:

    def login(self, db: Session, email: str, senha: str):
        usuario = usuario_service.buscar_por_email(db, email)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )

        if not SenhaHasher.verificar_senha(senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )

        token = jwt.create_access_token(user_id=usuario.id)

        return {
            "access_token": token,
            "token_type": "bearer"
        }
