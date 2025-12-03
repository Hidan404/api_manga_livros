from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.livro_schemas import LivroCreate, LivroUpdate
from app.controllers.livro_controller import LivroController
from app.core.dependecia_auth import require_role
from app.utils.dependecias_utils import get_current_user

rota_livros = APIRouter(prefix="/livros", tags=["Livros"])


@rota_livros.get("/")
def listar_livros(db: Session = Depends(get_db)):
    return LivroController.listar(db)


@rota_livros.get("/{livro_id}")
def obter_livro(livro_id: int, db: Session = Depends(get_db)):
    return LivroController.obter_por_id(db, livro_id)


# Somente ADMIN pode criar livro
@rota_livros.post("/", dependencies=[Depends(require_role("admin"))])
def criar_livro(
    dados: LivroCreate,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return LivroController.criar(db, dados)


# Somente ADMIN pode atualizar livro
@rota_livros.put("/{livro_id}", dependencies=[Depends(require_role("admin"))])
def atualizar_livro(
    livro_id: int,
    dados: LivroUpdate,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return LivroController.atualizar(db, livro_id, dados)


# Somente ADMIN pode deletar
@rota_livros.delete("/{livro_id}", dependencies=[Depends(require_role("admin"))])
def deletar_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return LivroController.deletar(db, livro_id)
