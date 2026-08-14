"""Conexão com o banco de dados (Sprint 1).

Mudanças:
- Lê a URL do banco e o modo SSL da configuração central (`config`),
  eliminando o `sslmode=require` hardcoded que quebrava ambientes sem SSL.
- Remove `load_dotenv()` daqui: o `config` (pydantic-settings) já carrega o `.env`.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.configuracao import config

# URL completa vem da configuração (ambiente ou .env)
SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

# sslmode é específico do PostgreSQL (Supabase exige require; local disable).
# Para outros dialetos (ex.: SQLite nos testes), não passamos connect_args.
connect_args: dict = {}
if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    connect_args["sslmode"] = config.SSL_MODE

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Função de diagnóstico (opcional, só para debug)
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
