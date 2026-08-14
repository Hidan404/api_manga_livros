from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.controllers.manga_controller import MangaController
from app.controllers.manga_volume_controller import MangaVolumeController
from app.core.dependecia_auth import get_current_user, require_role
from app.database.conexao import get_db
from app.schemas.manga_schemas import (
    MangaCreate,
    MangaResponse,
    MangaUpdate,
    VolumeCreate,
    VolumeResponse,
    VolumeUpdate,
)

rota_mangas = APIRouter(prefix="/mangas", tags=["Mangas"])


@rota_mangas.get("/", summary="Listar mangas", description="Retorna uma lista de todos os mangas disponíveis.", response_model=list[MangaResponse])
def listar_mangas(db: Session = Depends(get_db)):
    return MangaController.listar(db)


@rota_mangas.get("/{manga_id}", summary="Obter manga", description="Retorna os detalhes de um manga específico.", response_model=MangaResponse)
def obter_manga(manga_id: int, db: Session = Depends(get_db)):
    return MangaController.obter_por_id(db, manga_id)


# Somente ADMIN pode criar
@rota_mangas.post("/", summary="Criar manga", description="Cria um novo manga com os dados fornecidos.", dependencies=[Depends(require_role("admin"))], status_code=201, response_model=MangaResponse)
def criar_manga(
    dados: MangaCreate,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return MangaController.criar(db, dados)


# Somente ADMIN pode atualizar
@rota_mangas.put("/{manga_id}", summary="Atualizar manga", description="Atualiza os dados de um manga específico.", dependencies=[Depends(require_role("admin"))], response_model=MangaResponse)
def atualizar_manga(
    manga_id: int,
    dados: MangaUpdate,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return MangaController.atualizar(db, manga_id, dados)


# Somente ADMIN pode deletar
@rota_mangas.delete("/{manga_id}", summary="Deletar manga", description="Remove um manga específico do sistema.", dependencies=[Depends(require_role("admin"))])
def deletar_manga(
    manga_id: int,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return MangaController.deletar(db, manga_id)


@rota_mangas.post("/{manga_id}/upload-capa", summary="Upload de capa de manga", description="Faz upload da capa de um manga específico.", dependencies=[Depends(require_role("admin"))])
def upload_capa_manga(
    manga_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return MangaController.upload_capa(db, manga_id, arquivo)


@rota_mangas.post("/{manga_id}/volumes/{numero}/upload-capa", summary="Upload de capa de volume", description="Faz upload da capa de um volume específico.", dependencies=[Depends(require_role("admin"))])
def upload_capa_volume(
    manga_id: int,
    numero: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return MangaVolumeController.upload_capa_volume(db, manga_id, numero, arquivo)


@rota_mangas.get("/{manga_id}/volumes", summary="Listar volumes", description="Retorna uma lista de todos os volumes de um manga específico.", response_model=list[VolumeResponse])
def listar_volumes(manga_id: int, db: Session = Depends(get_db)):
    return MangaVolumeController.listar_volumes(db, manga_id)


@rota_mangas.get("/{manga_id}/volumes/{numero}", summary="Obter volume", description="Retorna os detalhes de um volume específico de um manga.", response_model=VolumeResponse)
def obter_volume(manga_id: int, numero: int, db: Session = Depends(get_db)):
    return MangaVolumeController.obter_volume(db, manga_id, numero)


@rota_mangas.put("/{manga_id}/volumes/{numero}", summary="Atualizar volume", description="Atualiza os dados de um volume específico de um manga.", response_model=VolumeResponse)
def atualizar_volume(manga_id: int, numero: int, dados: VolumeUpdate, db: Session = Depends(get_db)):
    return MangaVolumeController.atualizar_volume(db, manga_id, numero, dados)


@rota_mangas.delete("/{manga_id}/volumes/{numero}", summary="Remover volume", description="Remove um volume específico de um manga.")
def remover_volume(manga_id: int, numero: int, db: Session = Depends(get_db)):
    return MangaVolumeController.remover_volume(db, manga_id, numero)


@rota_mangas.post("/{manga_id}/volumes", summary="Adicionar volume", description="Cria um novo volume para um manga específico.", status_code=201, dependencies=[Depends(require_role("admin"))], response_model=VolumeResponse)
def adicionar_volume(manga_id: int, volume: VolumeCreate, db: Session = Depends(get_db)):
    return MangaVolumeController.adicionar_volume(db, manga_id, volume)
