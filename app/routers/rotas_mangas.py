from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.manga_schemas import MangaCreate, MangaUpdate
from app.controllers.manga_controller import MangaController
from app.core.dependecia_auth import obter_usuario_logado, require_role

rota_mangas = APIRouter(prefix="/mangas", tags=["Mangas"])


@rota_mangas.get("/")
def listar_mangas(db: Session = Depends(get_db)):
    return MangaController.listar(db)


@rota_mangas.get("/{manga_id}")
def obter_manga(manga_id: int, db: Session = Depends(get_db)):
    return MangaController.obter_por_id(db, manga_id)


@rota_mangas.post("/", dependencies=[Depends(require_role("admin"))])
def criar_manga(dados: MangaCreate, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return MangaController.criar(db, dados)


@rota_mangas.put("/{manga_id}", dependencies=[Depends(require_role("admin"))])
def atualizar_manga(manga_id: int, dados: MangaUpdate, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return MangaController.atualizar(db, manga_id, dados)


@rota_mangas.delete("/{manga_id}", dependencies=[Depends(require_role("admin"))])
def deletar_manga(manga_id: int, db: Session = Depends(get_db), usuario_logado=Depends(obter_usuario_logado)):
    return MangaController.deletar(db, manga_id)
