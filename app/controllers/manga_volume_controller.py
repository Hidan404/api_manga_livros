from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.capa_upload import fazer_upload
from app.models.manga_model import Manga
from app.models.manga_volume_model import MangaVolume
from app.schemas.manga_schemas import VolumeCreate, VolumeUpdate


class MangaVolumeController:

    @staticmethod
    def adicionar_volume(db: Session, manga_id: int, dados: VolumeCreate):
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if not manga:
            raise HTTPException(status_code=404, detail="Mangá não encontrado")

        existe = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=dados.numero
        ).first()

        if existe:
            raise HTTPException(status_code=400, detail="Esse volume já existe")

        volume = MangaVolume(
            manga_id=manga_id,
            numero=dados.numero,
            comprado=dados.comprado
        )

        db.add(volume)
        db.commit()
        db.refresh(volume)
        return volume

    @staticmethod
    def listar_volumes(db: Session, manga_id: int):
        return db.query(MangaVolume).filter_by(manga_id=manga_id).order_by(MangaVolume.numero).all()

    @staticmethod
    def obter_volume(db: Session, manga_id: int, numero: int):
        volume = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if not volume:
            raise HTTPException(status_code=404, detail="Volume não encontrado")

        return volume

    @staticmethod
    def atualizar_volume(db: Session, manga_id: int, numero: int, dados: VolumeUpdate):
        volume = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if not volume:
            raise HTTPException(status_code=404, detail="Volume não encontrado")

        if dados.numero is not None and dados.numero != numero:
            conflito = db.query(MangaVolume).filter_by(
                manga_id=manga_id,
                numero=dados.numero
            ).first()
            if conflito:
                raise HTTPException(status_code=400, detail="Esse volume já existe")
            volume.numero = dados.numero

        if dados.comprado is not None:
            volume.comprado = dados.comprado
        if dados.capa_volume is not None:
            volume.capa_volume = dados.capa_volume

        db.commit()
        db.refresh(volume)
        return volume

    @staticmethod
    def remover_volume(db: Session, manga_id: int, numero: int):
        volume = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if not volume:
            raise HTTPException(status_code=404, detail="Volume não encontrado")

        db.delete(volume)
        db.commit()

        return {"detail": "Volume removido com sucesso"}

    @staticmethod
    def upload_capa_volume(db: Session, manga_id: int, numero: int, arquivo):
        volume = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if not volume:
            raise HTTPException(status_code=404, detail="Volume não encontrado")

        url = fazer_upload(arquivo, pasta=f"mangas/{manga_id}/volumes", public_id=str(numero))
        volume.capa_volume = url

        db.commit()
        db.refresh(volume)
        return {"mensagem": "Capa do volume atualizada com sucesso.", "capa_url": url}
