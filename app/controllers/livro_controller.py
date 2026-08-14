from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.capa_upload import fazer_upload
from app.models.livros_model import Livro
from app.schemas.livro_schemas import LivroCreate, LivroUpdate


class LivroController:

    @staticmethod
    def listar(db: Session):
        return db.query(Livro).all()

    @staticmethod
    def obter_por_id(db: Session, livro_id: int):
        livro = db.query(Livro).filter(Livro.id == livro_id).first()
        if not livro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado."
            )
        return livro

    @staticmethod
    def criar(db: Session, dados: LivroCreate):
        novo = Livro(**dados.model_dump())
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    @staticmethod
    def atualizar(db: Session, livro_id: int, dados: LivroUpdate):
        livro = LivroController.obter_por_id(db, livro_id)

        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(livro, campo, valor)

        db.commit()
        db.refresh(livro)
        return livro

    @staticmethod
    def deletar(db: Session, livro_id: int):
        livro = LivroController.obter_por_id(db, livro_id)
        # Favoritos são removidos automaticamente (FKs ON DELETE CASCADE).
        db.delete(livro)
        db.commit()
        return {"mensagem": "Livro removido com sucesso."}

    @staticmethod
    def upload_capa(db: Session, livro_id: int, arquivo):
        livro = LivroController.obter_por_id(db, livro_id)
        url = fazer_upload(arquivo, pasta="livros", public_id=str(livro.id))
        livro.capa_url = url
        db.commit()
        db.refresh(livro)
        return {"mensagem": "Capa do livro atualizada com sucesso.", "capa_url": url}
