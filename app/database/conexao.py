from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ ENGINE (criado direto, sem retry no import) apelei para ia nessa
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ✅ função de conexão (opcional, só para debug) kkk
def testar_conexao():
    try:
        conn = engine.connect()
        conn.close()
        print("✅ Banco conectado!")
    except Exception as e:
        print("❌ Erro ao conectar no banco:", e)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()