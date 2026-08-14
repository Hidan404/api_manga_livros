from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.favoritos_controller import FavoritoMangaController
from app.core.dependecia_auth import get_current_user
from app.database.conexao import get_db
from app.schemas.favoritos_schemas import FavoritoMangaResponse

rota_favoritos_manga = APIRouter(prefix="/favoritos/manga", tags=["Favoritos - Manga"])

@rota_favoritos_manga.post("/{manga_id}", summary="Adicionar manga aos favoritos", description="Adiciona um manga à lista de favoritos do usuário autenticado.", response_model=FavoritoMangaResponse)
def adicionar_favorito(manga_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.adicionar_favorito(db, usuario["id"], manga_id)

@rota_favoritos_manga.delete("/{favorito_id}", summary="Remover manga dos favoritos", description="Remove um manga da lista de favoritos do usuário autenticado.")
def remover_favorito(favorito_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.remover_favorito(db, usuario["id"], favorito_id)


@rota_favoritos_manga.get("/", summary="Listar mangás favoritos", description="Lista os mangás favoritos do usuário autenticado.", response_model=list[FavoritoMangaResponse])
def listar_favoritos(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.listar_favoritos(db, usuario["id"])
