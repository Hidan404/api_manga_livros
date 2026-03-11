from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.manga_model import Manga
from app.models.favoritos_model import UsuarioFavoritoManga
from app.schemas.manga_schemas import MangaCreate, MangaUpdate


class MangaController:

    @staticmethod
    def listar(db: Session):
        return db.query(Manga).all()

    @staticmethod
    def obter_por_id(db: Session, manga_id: int):
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if not manga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mangá não encontrado."
            )
        return manga

    @staticmethod
    def criar(db: Session, dados: MangaCreate):
        novo = Manga(**dados.model_dump())
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    @staticmethod
    def atualizar(db: Session, manga_id: int, dados: MangaUpdate):
        manga = MangaController.obter_por_id(db, manga_id)

        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(manga, campo, valor)

        db.commit()
        db.refresh(manga)
        return manga

    @staticmethod
    def deletar(db: Session, manga_id: int):
        manga = MangaController.obter_por_id(db, manga_id)
        db.query(UsuarioFavoritoManga).filter(UsuarioFavoritoManga.manga_id == manga_id).delete()
        db.delete(manga)
        db.commit()
        return {"mensagem": "Mangá removido com sucesso."}
    
    @staticmethod
    def upload_capa(db: Session, manga_id: int, arquivo):
        manga = MangaController.obter_por_id(db, manga_id)
        conteudo = arquivo.file.read()
        manga.capa_url = conteudo
        db.commit()
        db.refresh(manga)
        return {"mensagem": "Capa do mangá atualizada com sucesso."}
