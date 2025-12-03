from fastapi import APIRouter, Depends, HTTPException
from app.controllers.favoritos_controller import FavoritoLivroController
from app.utils.dependecias_utils import get_current_user
#Todo: criar controller para favoritos de livros
routa_favoritos_livros = APIRouter(prefix="/favoritos/livros", tags=["Favoritos - Livros"])


@routa_favoritos_livros.post("/", dependencies=[Depends(get_current_user)])
def adicionar_favorito_livro(livro_id: int, usuario=Depends(get_current_user)):
    return FavoritoLivroController.adicionar_favorito(usuario["id"], livro_id)


@routa_favoritos_livros.get("/", dependencies=[Depends(get_current_user)])
def listar_favoritos_livros(usuario=Depends(get_current_user)):
    return FavoritoLivroController.listar_favoritos(usuario["id"])


@routa_favoritos_livros.delete("/{favorito_id}", dependencies=[Depends(get_current_user)])
def remover_favorito_livro(favorito_id: int, usuario=Depends(get_current_user)):
    return FavoritoLivroController.remover_favorito(usuario["id"], favorito_id)
