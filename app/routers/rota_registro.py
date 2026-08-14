from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.roles import RoleUsuario
from app.database.conexao import get_db
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCriar
from app.utils.senha_hasher import SenhaHasher

rota = APIRouter(prefix="/auth")


@rota.post("/register", summary="Registrar novo usuário",
           description="Cria um novo usuário com role=user (admin é criado apenas via seed).")
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    senha_hashe = SenhaHasher()
    senha_hash = senha_hashe.hash_criar(dados.senha)

    # Nunca confiar em role vinda do cliente: todo registro é role=user.
    # Para criar um admin, usar o script `seed_admin.py`.
    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=senha_hash,
        role=RoleUsuario.USER.value,
    )
    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado."
        ) from None
    return {"msg": "Usuário criado com sucesso"}
