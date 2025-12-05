from sqlalchemy.orm import Session
from fastapi import HTTPException, status
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
        novo = Livro(
            titulo=dados.titulo,
            autor=dados.autor,
            sinopse=dados.descricao,
            ano=dados.ano,
            genero=dados.genero
    )
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
        db.delete(livro)
        db.commit()
        return {"mensagem": "Livro removido com sucesso."}
