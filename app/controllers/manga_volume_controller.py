from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.manga_model import Manga
from app.models.manga_volume_model import MangaVolume


class MangaVolumeController:

    @staticmethod
    def adicionar_volume(db: Session, manga_id: int, numero: int):

        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if not manga:
            raise HTTPException(status_code=404, detail="Mangá não encontrado")

        existe = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if existe:
            raise HTTPException(status_code=400, detail="Esse volume já existe")

        volume = MangaVolume(
            manga_id=manga_id,
            numero=numero,
            comprado=True
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
    def atualizar_volume(db: Session, manga_id: int, numero: int, comprado: bool):

        volume = db.query(MangaVolume).filter_by(
            manga_id=manga_id,
            numero=numero
        ).first()

        if not volume:
            raise HTTPException(status_code=404, detail="Volume não encontrado")

        volume.comprado = comprado

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

        conteudo = arquivo.file.read()
        volume.capa_volume = conteudo

        db.commit()
        db.refresh(volume)
        return {"mensagem": "Capa do volume atualizada com sucesso."}

