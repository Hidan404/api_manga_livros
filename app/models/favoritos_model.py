from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.conexao import Base


class UsuarioFavoritoLivro(Base):
    __tablename__ = "usuarios_favoritos_livros"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    livro_id = Column(Integer, ForeignKey("livros.id"))

    usuario = relationship("Usuario", back_populates="favoritos_livros")
    livro = relationship("Livro")


class UsuarioFavoritoManga(Base):
    __tablename__ = "usuarios_favoritos_mangas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    manga_id = Column(Integer, ForeignKey("mangas.id"))

    usuario = relationship("Usuario", back_populates="favoritos_mangas")
    manga = relationship("Manga")
