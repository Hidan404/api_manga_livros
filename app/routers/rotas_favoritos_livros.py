from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexao import get_db
from app.controllers.favoritos_controller import FavoritoLivroController
from app.utils.dependecias_utils import get_current_user

routa_favoritos_livros = APIRouter(prefix="/favoritos/livros", tags=["Favoritos - Livros"])


@routa_favoritos_livros.post("/{livro_id}")
def adicionar_favorito_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.adicionar_favorito(db, usuario["id"], livro_id)


@routa_favoritos_livros.get("/")
def listar_favoritos_livros(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.listar_favoritos(usuario["id"], db)


@routa_favoritos_livros.delete("/{favorito_id}")
def remover_favorito_livro(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.remover_favorito(usuario["id"], favorito_id, db)
