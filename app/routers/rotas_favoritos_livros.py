from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexao import get_db
from app.controllers.favoritos_controller import FavoritoLivroController
from app.utils.dependecias_utils import get_current_user

routa_favoritos_livros = APIRouter(prefix="/favoritos/livros", tags=["Favoritos - Livros"])


@routa_favoritos_livros.post("/{livro_id}", summary="Adicionar livro aos favoritos", description="Adiciona um livro à lista de favoritos do usuário autenticado.")
def adicionar_favorito_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.adicionar_favorito(db, usuario["id"], livro_id)


@routa_favoritos_livros.get("/", summary="Listar livros favoritos", description="Lista os livros favoritos do usuário autenticado.")
def listar_favoritos_livros(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.listar_favoritos(usuario["id"], db)


@routa_favoritos_livros.delete("/{favorito_id}", summary="Remover livro dos favoritos", description="Remove um livro da lista de favoritos do usuário autenticado.")
def remover_favorito_livro(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.remover_favorito(usuario["id"], favorito_id, db)
