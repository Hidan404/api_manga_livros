from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.conexao import Base




class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer,primary_key=True, index=True)
    nome = Column(String(100),nullable=False)
    email = Column(String(100),unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")

    favoritos_livros = relationship("UsuarioFavoritoLivro", back_populates="usuario")
    favoritos_mangas = relationship("UsuarioFavoritoManga", back_populates="usuario")
