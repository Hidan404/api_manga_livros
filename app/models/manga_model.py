from sqlalchemy import Column, Integer, String, Text, Date
from app.database.conexao import Base

class Manga(Base):
    __tablename__ = "mangas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    artista = Column(String(255), nullable=True)
    genero = Column(String(100), nullable=False)
    volumes = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False)  
    data_lancamento = Column(Date, nullable=True)
    sinopse = Column(Text, nullable=True)
    capa_url = Column(String(500), nullable=True)
