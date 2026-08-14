from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class MangaVolume(Base):
    __tablename__ = "manga_volumes"
    __table_args__ = (
        UniqueConstraint("manga_id", "numero", name="uq_manga_volumes_manga_numero"),
    )

    id = Column(Integer, primary_key=True, index=True)
    manga_id = Column(
        Integer, ForeignKey("mangas.id", ondelete="CASCADE"), nullable=False
    )
    numero = Column(Integer, nullable=False)
    comprado = Column(Boolean, default=True)
    capa_volume = Column(String(500), nullable=True)  # URL ou caminho para a capa do volume

    manga = relationship("Manga", back_populates="volumes")
