from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class UsuarioFavoritoLivro(Base):
    __tablename__ = "usuarios_favoritos_livros"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "livro_id", name="uq_favorito_livro_usuario_livro"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    livro_id = Column(
        Integer, ForeignKey("livros.id", ondelete="CASCADE"), nullable=False
    )

    usuario = relationship("Usuario", back_populates="favoritos_livros")
    livro = relationship("Livro")


class UsuarioFavoritoManga(Base):
    __tablename__ = "usuarios_favoritos_mangas"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "manga_id", name="uq_favorito_manga_usuario_manga"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    manga_id = Column(
        Integer, ForeignKey("mangas.id", ondelete="CASCADE"), nullable=False
    )

    usuario = relationship("Usuario", back_populates="favoritos_mangas")
    manga = relationship("Manga")
