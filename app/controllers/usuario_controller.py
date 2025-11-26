from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.senha_hasher import SenhaHasher
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCriar

class UsuarioController:

    def criar_usuario(self, db: Session, dados: UsuarioCriar):
        usuario_existente = db.query(Usuario).filter(Usuario.email == dados.email).first()

        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está cadastrado."
            )

        senha_hash = SenhaHasher.criar_hash(dados.senha)

        novo_usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha_hash=senha_hash
        )

        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        return novo_usuario

    def buscar_por_email(self, db: Session, email: str):
        return db.query(Usuario).filter(Usuario.email == email).first()
