from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.roles import RoleUsuario
from app.database.conexao import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    # Default agora vem do registro central de roles (extensível para micro-SaaS)
    role = Column(String(50), nullable=False, default=RoleUsuario.USER.value)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True, server_default="true")

    favoritos_livros = relationship("UsuarioFavoritoLivro", back_populates="usuario")
    favoritos_mangas = relationship("UsuarioFavoritoManga", back_populates="usuario")
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
