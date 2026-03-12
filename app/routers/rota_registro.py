from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexao import get_db
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCriar
from app.utils.senha_hasher import SenhaHasher
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


rota = APIRouter(prefix="/auth")

@rota.post("/register", summary="Registrar novo usuário", description="Cria um novo usuário com email e senha.")
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    senha_hashe = SenhaHasher()
    senha_hash = senha_hashe.hash_criar(dados.senha)

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=senha_hash,
        #role=dados.role
        role = "admin"
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
        )
    return {"msg": "Usuário criado com sucesso"}
