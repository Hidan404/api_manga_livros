from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.manga_schemas import MangaCreate, MangaUpdate
from app.controllers.manga_controller import MangaController

rota_mangas = APIRouter(prefix="/mangas", tags=["Mangas"])


@rota_mangas.get("/")
def listar_mangas(db: Session = Depends(get_db)):
    return MangaController.listar(db)


@rota_mangas.get("/{manga_id}")
def obter_manga(manga_id: int, db: Session = Depends(get_db)):
    return MangaController.obter_por_id(db, manga_id)


@rota_mangas.post("/")
def criar_manga(dados: MangaCreate, db: Session = Depends(get_db)):
    return MangaController.criar(db, dados)


@rota_mangas.put("/{manga_id}")
def atualizar_manga(manga_id: int, dados: MangaUpdate, db: Session = Depends(get_db)):
    return MangaController.atualizar(db, manga_id, dados)


@rota_mangas.delete("/{manga_id}")
def deletar_manga(manga_id: int, db: Session = Depends(get_db)):
    return MangaController.deletar(db, manga_id)
