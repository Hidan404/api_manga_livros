from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.favoritos_controller import FavoritoMangaController
from app.database.conexao import get_db
from app.utils.dependecias_utils import get_current_user

router = APIRouter(prefix="/favoritos/mangas", tags=["Favoritos - Mangás"])


@router.post("/")
def adicionar(manga_id: int, usuario=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoritoMangaController.adicionar_favorito(usuario["id"], manga_id, db)


@router.get("/")
def listar(usuario=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoritoMangaController.listar_favoritos(usuario["id"], db)


@router.delete("/{favorito_id}")
def remover(favorito_id: int, usuario=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoritoMangaController.remover_favorito(usuario["id"], favorito_id, db)
