from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.livro_schemas import LivroCreate, LivroUpdate
from app.controllers.livro_controller import LivroController
from app.core.dependecia_auth import obter_usuario_logado, require_role

rota_livros = APIRouter(prefix="/livros", tags=["Livros"])


@rota_livros.get("/")
def listar_livros(db: Session = Depends(get_db)):
    return LivroController.listar(db)


@rota_livros.get("/{livro_id}")
def obter_livro(livro_id: int, db: Session = Depends(get_db)):
    return LivroController.obter_por_id(db, livro_id)


@rota_livros.post("/", dependencies=[Depends(require_role("admin"))])
def criar_livro(dados: LivroCreate, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return LivroController.criar(db, dados)


@rota_livros.put("/{livro_id}", dependencies=)
def atualizar_livro(livro_id: int, dados: LivroUpdate, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return LivroController.atualizar(db, livro_id, dados)


@rota_livros.delete("/{livro_id}", dependencies=[Depends(require_role("admin"))])
def deletar_livro(livro_id: int, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return LivroController.deletar(db, livro_id)
