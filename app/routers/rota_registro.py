from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexao import get_db
from app.models.usuario_model import Usuario
from app.schemas.autentica_schemas import LoginSchema
from app.utils.senha_hasher import SenhaHasher

rota = APIRouter(prefix="/auth")

@rota.post("/register")
def registrar(dados: LoginSchema, db: Session = Depends(get_db)):
    senha_hashe = SenhaHasher()
    senha_hash = senha_hashe.hash_criar(dados.senha)

    novo_usuario = Usuario(
        email=dados.email,
        senha=senha_hash
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {"msg": "Usuário criado com sucesso"}
