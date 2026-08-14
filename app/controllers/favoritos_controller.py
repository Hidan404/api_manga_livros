from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.favoritos_model import UsuarioFavoritoLivro, UsuarioFavoritoManga
from app.models.livros_model import Livro
from app.models.manga_model import Manga


def _serializar_livro(favorito: UsuarioFavoritoLivro) -> dict:
    return {
        "id": favorito.id,
        "usuario_id": favorito.usuario_id,
        "livro_id": favorito.livro_id,
        "titulo": favorito.livro.titulo,
    }


def _serializar_manga(favorito: UsuarioFavoritoManga) -> dict:
    return {
        "id": favorito.id,
        "usuario_id": favorito.usuario_id,
        "manga_id": favorito.manga_id,
        "titulo": favorito.manga.titulo,
    }


class FavoritoLivroController:

    @staticmethod
    def adicionar_favorito(db: Session, usuario_id: int, livro_id: int):
        livro = db.query(Livro).filter(Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        ja_existe = db.query(UsuarioFavoritoLivro).filter_by(
            usuario_id=usuario_id,
            livro_id=livro_id
        ).first()

        if ja_existe:
            raise HTTPException(status_code=400, detail="Livro já está nos favoritos")

        favorito = UsuarioFavoritoLivro(
            usuario_id=usuario_id,
            livro_id=livro_id
        )

        db.add(favorito)
        db.commit()
        db.refresh(favorito)

        return _serializar_livro(favorito)

    @staticmethod
    def listar_favoritos(usuario_id: int, db: Session):
        favoritos = db.query(UsuarioFavoritoLivro).filter_by(usuario_id=usuario_id).all()
        return [_serializar_livro(f) for f in favoritos]

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
        return {"msg": "Favorito removido com sucesso"}


class FavoritoMangaController:

    @staticmethod
    def adicionar_favorito(db: Session, usuario_id: int, manga_id: int):
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if not manga:
            raise HTTPException(status_code=404, detail="Manga não encontrado")

        ja_existe = db.query(UsuarioFavoritoManga).filter_by(
            usuario_id=usuario_id,
            manga_id=manga_id
        ).first()

        if ja_existe:
            raise HTTPException(status_code=400, detail="Manga já está nos favoritos")

        favorito = UsuarioFavoritoManga(
            usuario_id=usuario_id,
            manga_id=manga_id
        )

        db.add(favorito)
        db.commit()
        db.refresh(favorito)

        return _serializar_manga(favorito)

    @staticmethod
    def listar_favoritos(db: Session, usuario_id: int):
        favoritos = db.query(UsuarioFavoritoManga).filter_by(usuario_id=usuario_id).all()
        return [_serializar_manga(f) for f in favoritos]

    @staticmethod
    def remover_favorito(db: Session, usuario_id: int, favorito_id: int):
        favorito = db.query(UsuarioFavoritoManga).filter_by(
            usuario_id=usuario_id,
            id=favorito_id
        ).first()

        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito não encontrado")

        db.delete(favorito)
        db.commit()
        return {"msg": "Favorito removido com sucesso"}
