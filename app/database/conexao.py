from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import time

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 Função que espera o banco subir
def criar_engine_com_retry():
    for i in range(10):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            connection = engine.connect()
            connection.close()
            print("✅ Banco conectado!")
            return engine
        except Exception as e:
            print(f"⏳ Tentando conectar no banco... ({i+1}/10)")
            time.sleep(3)
    
    raise Exception("❌ Não conseguiu conectar no banco")

# usa o retry aqui
criacao = criar_engine_com_retry()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=criacao
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
