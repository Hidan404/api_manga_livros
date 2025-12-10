from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.conexao import Base

class MangaVolume(Base):
    __tablename__ = "manga_volumes"

    id = Column(Integer, primary_key=True, index=True)
    manga_id = Column(Integer, ForeignKey("mangas.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    comprado = Column(Boolean, default=True)

    manga = relationship("Manga", back_populates="volumes")
