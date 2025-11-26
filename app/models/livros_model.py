from sqlalchemy import Column, Integer, String, Date, Text
from app.database.conexao import Base

class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    genero = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    data_publicacao = Column(Date, nullable=True)
    sinopse = Column(Text, nullable=True)
    capa_url = Column(String(500), nullable=True)
    criado_em = Column(Date, nullable=False)