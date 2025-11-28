from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.conexao import get_db
from app.models.favoritos_model import UsuarioFavoritoLivro, UsuarioFavoritoManga
from app.models.livros_model import Livro
from app.models.manga_model import Manga


class FavoritoLivroController:

    @staticmethod
    def adicionar_favorito(usuario_id: int, livro_id: int, db: Session):
        livro = db.query(Livro).filter(Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        ja_existe = db.query(UsuarioFavoritoLivro).filter_by(
            usuario_id=usuario_id,
            livro_id=livro_id
        ).first()

        if ja_existe:
            raise HTTPException(status_code=400, detail="Livro já está nos favoritos")

        favorito = UsuarioFavoritoLivro(usuario_id=usuario_id, livro_id=livro_id)
        db.add(favorito)
        db.commit()
        db.refresh(favorito)
        return favorito

    @staticmethod
    def listar_favoritos(usuario_id: int, db: Session):
        return db.query(UsuarioFavoritoLivro).filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def remover_favorito(usuario_id: int, favorito_id: int, db: Session):
        favorito = db.query(UsuarioFavoritoLivro).filter_by(
            usuario_id=usuario_id,
            id=favorito_id
        ).first()

        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito não encontrado")

        db.delete(favorito)
        db.commit()
        return {"detail": "Favorito removido com sucesso"}


class FavoritoMangaController:

    @staticmethod
    def adicionar_favorito(usuario_id: int, manga_id: int, db: Session):
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if not manga:
            raise HTTPException(status_code=404, detail="Mangá não encontrado")

        ja_existe = db.query(UsuarioFavoritoManga).filter_by(
            usuario_id=usuario_id,
            manga_id=manga_id
        ).first()

        if ja_existe:
            raise HTTPException(status_code=400, detail="Mangá já está nos favoritos")

        favorito = UsuarioFavoritoManga(usuario_id=usuario_id, manga_id=manga_id)
        db.add(favorito)
        db.commit()
        db.refresh(favorito)
        return favorito

    @staticmethod
    def listar_favoritos(usuario_id: int, db: Session):
        return db.query(UsuarioFavoritoManga).filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def remover_favorito(usuario_id: int, favorito_id: int, db: Session):
        favorito = db.query(UsuarioFavoritoManga).filter_by(
            usuario_id=usuario_id,
            id=favorito_id
        ).first()

        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito não encontrado")

        db.delete(favorito)
        db.commit()

        return {"detail": "Favorito removido com sucesso"}
