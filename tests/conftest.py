"""Fixtures de teste (Sprint 6).

Banco isolado: SQLite em arquivo (tests/test_api.db), criado/destruído por sessão e
limpo entre testes. Sem dependência de credenciais reais (removido o `hidan@gmail.com`).

IMPORTANTE: as variáveis de ambiente são definidas ANTES de importar o app —
a configuração (pydantic-settings) é lida na importação e o env tem precedência
sobre o `.env`.
"""

import os
import uuid

import pytest

os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///./tests/test_api.db"
os.environ["SSL_MODE"] = "disable"
# setdefault preserva o valor real em CI (secret CLOUDINARY_URL); localmente fica vazio.
os.environ.setdefault("CLOUDINARY_URL", "")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event  # noqa: E402

from app.core.rate_limit import limiter  # noqa: E402
from app.core.roles import RoleUsuario  # noqa: E402
from app.database.conexao import Base, SessionLocal, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.usuario_model import Usuario  # noqa: E402
from app.utils.senha_hasher import SenhaHasher  # noqa: E402

# Rate limit desativado nos testes: o slowapi conta por IP e o TestClient usa
# sempre o mesmo endereço ("testclient"), o que estouraria "10/minute" no login.
limiter.enabled = False

# SQLite não aplica FKs por padrão; ativa o CASCADE (essencial p/ testes de deleção).
_engine_teste = SessionLocal().bind


@event.listens_for(_engine_teste, "connect")
def _ativar_foreign_keys(dbapi_conn, _record):  # pragma: no cover
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


CAMINHO_BANCO = "tests/test_api.db"


def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def _banco_teste():
    if os.path.exists(CAMINHO_BANCO):
        os.remove(CAMINHO_BANCO)
    engine = SessionLocal().bind
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(CAMINHO_BANCO):
        os.remove(CAMINHO_BANCO)


@pytest.fixture(autouse=True)
def _limpar_tabelas():
    """Isolamento: zera todas as tabelas após cada teste."""
    yield
    session = SessionLocal()
    try:
        for tabela in reversed(Base.metadata.sorted_tables):
            session.execute(tabela.delete())
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_credenciais(client):
    """Cria o usuário admin direto no banco e retorna email/senha."""
    senha = "admin-secreto-123"
    admin = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        senha=SenhaHasher.hash_criar(senha),
        role=RoleUsuario.ADMIN.value,
    )
    session = SessionLocal()
    try:
        session.add(admin)
        session.commit()
        email = admin.email  # acesso após commit recarrega; deve ser antes de fechar
    finally:
        session.close()
    return {"email": email, "senha": senha}


@pytest.fixture
def admin_headers(client, admin_credenciais):
    """Token de acesso do admin (via API — login de verdade)."""
    resposta = client.post("/auth/login", json=admin_credenciais)
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def user_headers(client):
    """Token de acesso de um usuário comum (register + login)."""
    email = f"user-{uuid.uuid4().hex[:8]}@teste.com"
    registro = client.post("/auth/register", json={
        "nome": "Usuário Teste", "email": email, "senha": "123456",
    })
    assert registro.status_code == 200, registro.text
    login = client.post("/auth/login", json={"email": email, "senha": "123456"})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}
