from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.manga_schemas import MangaCreate, MangaUpdate
from app.controllers.manga_controller import MangaController
from app.core.dependecia_auth import require_role
from app.utils.dependecias_utils import get_current_user

rota_mangas = APIRouter(prefix="/mangas", tags=["Mangas"])


@rota_mangas.get("/")
def listar_mangas(db: Session = Depends(get_db)):
    return MangaController.listar(db)


@rota_mangas.get("/{manga_id}")
def obter_manga(manga_id: int, db: Session = Depends(get_db)):
    return MangaController.obter_por_id(db, manga_id)


# Somente ADMIN pode criar
@rota_mangas.post("/", dependencies=[Depends(require_role("admin"))])
def criar_manga(
    dados: MangaCreate,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return MangaController.criar(db, dados)


# Somente ADMIN pode atualizar
@rota_mangas.put("/{manga_id}", dependencies=[Depends(require_role("admin"))])
def atualizar_manga(
    manga_id: int,
    dados: MangaUpdate,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return MangaController.atualizar(db, manga_id, dados)


# Somente ADMIN pode deletar
@rota_mangas.delete("/{manga_id}", dependencies=[Depends(require_role("admin"))])
def deletar_manga(
    manga_id: int,
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return MangaController.deletar(db, manga_id)
