from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.controllers.favoritos_controller import FavoritoMangaController
from app.utils.dependecias_utils import get_current_user

rota_favoritos_manga = APIRouter(prefix="/favoritos/manga", tags=["Favoritos - Manga"])

@rota_favoritos_manga.post("/{manga_id}")
def adicionar_favorito(manga_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.adicionar(db, usuario.id, manga_id)

@rota_favoritos_manga.delete("/{manga_id}")
def remover_favorito(manga_id: int, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.remover(db, usuario.id, manga_id)

@rota_favoritos_manga.get("/")
def listar_favoritos(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return FavoritoMangaController.listar(db, usuario.id)
