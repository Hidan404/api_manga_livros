from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.favoritos_controller import FavoritoLivroController
from app.core.dependecia_auth import get_current_user
from app.database.conexao import get_db
from app.schemas.favoritos_schemas import FavoritoLivroResponse

rota_favoritos_livros = APIRouter(prefix="/favoritos/livros", tags=["Favoritos - Livros"])


@rota_favoritos_livros.post("/{livro_id}", summary="Adicionar livro aos favoritos", description="Adiciona um livro à lista de favoritos do usuário autenticado.", response_model=FavoritoLivroResponse)
def adicionar_favorito_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.adicionar_favorito(db, usuario["id"], livro_id)


@rota_favoritos_livros.get("/", summary="Listar livros favoritos", description="Lista os livros favoritos do usuário autenticado.", response_model=list[FavoritoLivroResponse])
def listar_favoritos_livros(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.listar_favoritos(usuario["id"], db)


@rota_favoritos_livros.delete("/{favorito_id}", summary="Remover livro dos favoritos", description="Remove um livro da lista de favoritos do usuário autenticado.")
def remover_favorito_livro(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return FavoritoLivroController.remover_favorito(usuario["id"], favorito_id, db)
