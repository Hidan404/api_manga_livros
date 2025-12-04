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

        if not SenhaHasher.verificar_senha(senha, usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )

        token = jwt.create_access_token(
            user_id=usuario.id,
            role=usuario.role   # 🔴 ISSO AQUI É O MAIS IMPORTANTE
        )   

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": usuario.role    
        }

    
    @staticmethod
    def refresh_token(refresh_token: str, db: Session):
        jwtm = Autenticacao_config()
        payload = jwtm.verificar_refresh_token(refresh_token)

        if not payload:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        user_id = int(payload["sub"])

        new_access = jwtm.create_access_token(user_id)
        return {"access_token": new_access, "token_type": "bearer"}

