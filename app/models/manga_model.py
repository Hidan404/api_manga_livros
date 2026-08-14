from sqlalchemy import Column, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Manga(Base):
    __tablename__ = "mangas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    artista = Column(String(255), nullable=True)
    genero = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    data_lancamento = Column(Date, nullable=True)
    sinopse = Column(Text, nullable=True)
    capa_url = Column(String(500), nullable=True)  # URL ou caminho para a capa do manga
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # Relacionamento com MangaVolume (lista de volumes de manga)
    volumes = relationship(
        "MangaVolume",
        back_populates="manga",
        cascade="all, delete"
    )

