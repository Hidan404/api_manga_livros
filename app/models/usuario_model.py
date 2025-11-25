from sqlalchemy import Column, Integer, String
from app.database.conexao import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer,primary_key=True, index=True)
    nome = Column(String(100),nullable=False)
    email = Column(String(100),unique=True, nullable=False)
    senha = Column(String(255), nullable=False)