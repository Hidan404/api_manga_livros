from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.schemas.manga_schemas import MangaCreate, MangaUpdate
from app.controllers.manga_controller import MangaController
from app.core.dependecia_auth import require_role
from app.utils.dependecias_utils import get_current_user
from app.controllers.manga_volume_controller import MangaVolumeController

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

@rota_mangas.post("/teste-admin")
def teste_admin(usuario_logado = Depends(get_current_user)):
    return {"usuario": usuario_logado}


@rota_mangas.post("/{manga_id}/upload-capa", dependencies=[Depends(require_role("admin"))])
def upload_capa_manga(
    manga_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    return MangaController.upload_capa(db, manga_id, arquivo)



@rota_mangas.post("/{manga_id}/volumes/{numero}/upload-capa", dependencies=[Depends(require_role("admin"))])
def upload_capa_volume(
    manga_id: int,
    numero: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_logado = Depends(get_current_user)
):
    
    return MangaVolumeController.upload_capa_volume(db, manga_id, numero, arquivo)


@rota_mangas.get("/{manga_id}/volumes")
def listar_volumes(manga_id: int, db: Session = Depends(get_db)):
    return MangaVolumeController.listar_volumes(db, manga_id)


@rota_mangas.get("/{manga_id}/volumes/{numero}")
def obter_volume(manga_id: int, numero: int, db: Session = Depends(get_db)):
    return MangaVolumeController.obter_volume(db, manga_id, numero)


@rota_mangas.put("/{manga_id}/volumes/{numero}")
def atualizar_volume(manga_id: int, numero: int, comprado: bool, db: Session = Depends(get_db)):
    return MangaVolumeController.atualizar_volume(db, manga_id, numero, comprado)

@rota_mangas.delete("/{manga_id}/volumes/{numero}")
def remover_volume(manga_id: int, numero: int, db: Session = Depends(get_db)):
    return MangaVolumeController.remover_volume(db, manga_id, numero)

@rota_mangas.post("/{manga_id}/volumes")
def adicionar_volume(manga_id: int, numero: int, db: Session = Depends(get_db)):
    return MangaVolumeController.adicionar_volume(db, manga_id, numero)