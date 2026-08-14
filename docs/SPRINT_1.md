# 🧱 Sprint 1 — Configuração e Conexão com o Banco

> Documento detalhado do que foi feito na Sprint 1.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Sprint anterior: [`SPRINT_0.md`](SPRINT_0.md)

---

## 1. Objetivo da Sprint 1

Fazer a aplicação **iniciar sem crash e sem side-effects**, com configuração centralizada,
SSL configurável, migrações versionadas (Alembic) e ambiente de desenvolvimento restaurado
em Python 3.11.

### Entregas planejadas
| Entrega | Status |
|---|---|
| `configuracao.py` com `ALGORITHM`, `ENVIRONMENT`, `SSL_MODE` e secrets validados | ✅ |
| `conexao.py` com sslmode configurável (remover hardcode `require`) | ✅ |
| Remover `Base.metadata.create_all` do import em `main.py` | ✅ |
| Alembic configurado + migração baseline das 6 tabelas | ✅ |
| Healthcheck + `depends_on: condition: service_healthy` no compose | ✅ |
| `.env` corrigido (typo `@@` e vars novas) | ✅ |
| Venv recriado em Python 3.11.8 + `requirements.txt` instalado | ✅ |

---

## 2. `app/core/configuracao.py` — configuração central

### 2.1. Código completo (versão final)

```python
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: Literal["development", "production"] = "development"

    DATABASE_URL: str
    SSL_MODE: Literal["disable", "require", "prefer", "allow"] = "disable"

    SECRET_KEY: str = ""
    REFRESH_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str = ""

    CLOUDINARY_URL: str = ""

    @model_validator(mode="after")
    def _validar_secrets(self) -> "Configuracao":
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY ausente ou muito curta em produção (mínimo 32 caracteres).")
            if not self.REFRESH_SECRET_KEY or len(self.REFRESH_SECRET_KEY) < 32:
                raise ValueError("REFRESH_SECRET_KEY ausente ou muito curta em produção (mínimo 32 caracteres).")
        else:
            self.SECRET_KEY = self.SECRET_KEY or "dev-secret-key-nao-usar-em-producao"
            self.REFRESH_SECRET_KEY = self.REFRESH_SECRET_KEY or "dev-refresh-secret-nao-usar-em-producao"
        return self


config = Configuracao()
```

### 2.2. Sintaxe e lógica

| Elemento | Explicação |
|---|---|
| `pydantic_settings.BaseSettings` | Lê variáveis do **ambiente** e do arquivo `.env` automaticamente — não precisa mais de `os.getenv` nem `load_dotenv()` manual. |
| `SettingsConfigDict(env_file=".env", extra="ignore")` | `env_file` aponta o arquivo local; `extra="ignore"` ignora chaves que não são campos da classe (ex.: `POSTGRES_*` do compose). |
| `Literal["development", "production"]` | Restringe o valor de `ENVIRONMENT` a essas 2 opções — erro de validação se vier algo diferente. |
| `DATABASE_URL: str` (sem default) | **Obrigatória** — se faltar, a classe falha ao instanciar (fail-fast no boot). |
| `SSL_MODE: Literal[...] = "disable"` | Controla o `sslmode` da conexão. `require` para Supabase; `disable` para local. |
| `model_validator(mode="after")` | Roda **depois** da validação dos campos. Em `production` exige secrets com ≥ 32 caracteres (derruba o boot se ausente). Em `development`, usa valores de dev claramente identificados. |
| `config = Configuracao()` | Instância global única usada pelo resto da aplicação. |

### 2.3. O que foi corrigido
- `ALGORITHM` agora é lido de verdade (antes estava no `.env` mas nunca usado → quebrava o refresh).
- Defaults fracos `"Ronald123"` / `"chave_refresh_secreta"` **removidos**.
- `SSL_MODE` e `ENVIRONMENT` criados (não existiam).
- Fim do `os.getenv` misturado com a classe.

### 2.4. Lib usada
- `pydantic-settings` (já estava no `requirements.txt`). **Nenhuma dependência nova.**

---

## 3. `app/database/conexao.py` — conexão com SSL configurável

### 3.1. Código completo (versão final)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.configuracao import config

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

connect_args = {"sslmode": config.SSL_MODE}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
```

### 3.2. O que mudou
- **Antes:** `connect_args={"sslmode": "require"}` hardcoded → quebrava local e Docker (Postgres sem SSL).
- **Agora:** `connect_args = {"sslmode": config.SSL_MODE}` — `require` para Supabase, `disable` para local.
- `load_dotenv()` removido daqui (o `config` já carrega o `.env`).
- `create_engine` **não conecta** até o primeiro uso (comportamento do SQLAlchemy) — logo, importar o app não depende do banco estar no ar.

---

## 4. `app/main.py` — fim do side-effect de criação de tabelas

### 4.1. Removido
```python
# ANTES (removido):
from app.database.conexao import Base, engine
...
Base.metadata.create_all(bind=engine)
```

### 4.2. Por quê
`create_all` no import:
- rodava a **todo import** (incluindo em testes);
- **não alterava** tabelas existentes (colunas novas nunca eram criadas);
- acoplava o boot ao banco.

O schema agora é gerenciado **exclusivamente pelo Alembic**.

---

## 5. Alembic — migrações versionadas

### 5.1. Setup
Comando: `alembic init alembic` → gerou `alembic.ini` + pasta `alembic/`.

### 5.2. `alembic/env.py` (editado)

```python
from app.core.configuracao import config as app_config
from app.database.conexao import Base
from app.models import (
    usuario_model,
    manga_model,
    manga_volume_model,
    livros_model,
    favoritos_model,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# A URL do banco vem da configuração da aplicação (ambiente / .env)
config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

target_metadata = Base.metadata
```

| Item | Lógica |
|---|---|
| `import` de todos os models | Garante que `Base.metadata` conheça as 6 tabelas (necessário para o `--autogenerate`). |
| `config.set_main_option("sqlalchemy.url", ...)` | A URL vem de **um só lugar** (a config da app), não do `alembic.ini`. |
| `prepend_sys_path = .` (em `alembic.ini`) | Permite `import app...` dentro do `env.py`. |

### 5.3. `alembic.ini`
- `script_location = %(here)s/alembic` (padrão)
- `prepend_sys_path = .` (padrão)
- `sqlalchemy.url` **comentado** — a URL vem do `env.py`.

### 5.4. Migração baseline `alembic/versions/baa3815000af_baseline_schema.py`

Gerada com `alembic revision --autogenerate -m "baseline schema"` contra um Postgres **vazio**.
Cria as 6 tabelas do schema atual (SPRINT 3 adicionará constraints e colunas novas):

| Tabela | Observações |
|---|---|
| `livros` | `isbn` unique, `criado_em` com `server_default=now()`, `capa_url` + `capa_livro` (duplicada — removida na Sprint 3) |
| `mangas` | sem timestamps (adicionados na Sprint 3) |
| `usuarios` | `email` unique, `role` string |
| `manga_volumes` | FK para `mangas`; **sem** unique `(manga_id, numero)` (Sprint 3) |
| `usuarios_favoritos_livros` | FKs nullable (Sprint 3: `nullable=False` + cascade) |
| `usuarios_favoritos_mangas` | idem |

### 5.5. Comandos úteis
```bash
alembic upgrade head     # aplica pendentes
alembic downgrade -1     # desfaz a última
alembic downgrade base   # volta ao estado vazio (tabelas removidas)
alembic current          # mostra a revisão atual
alembic check            # compara models com o banco (0 drift)
alembic upgrade head --sql  # modo offline (gera SQL sem conectar)
```

> **Banco que JÁ existe (produção/Supabase):** rodar `alembic stamp head`
> (marca a versão atual sem executar o CREATE). Só usar `upgrade head` se as
> tabelas ainda não existirem.

---

## 6. `docker-compose.yml` — healthcheck e dependência saudável

```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U usuario -d mangas_livros"]
    interval: 5s
    timeout: 5s
    retries: 10

api:
  environment:
    DATABASE_URL: postgresql+psycopg://usuario:senha@db:5432/mangas_livros
    SSL_MODE: disable
    ENVIRONMENT: development
  env_file:
    - .env
  depends_on:
    db:
      condition: service_healthy
```

| Item | Lógica |
|---|---|
| `healthcheck` com `pg_isready` | O Postgres só é considerado "pronto" quando aceita conexão. |
| `depends_on: db: condition: service_healthy` | A API **espera** o banco saudável antes de subir (antes podia crashar no boot). |
| `environment` da API sobrescreve `.env` | Dentro da rede do compose o banco é `db:5432`; fora (local), o `.env` usa `localhost:5434`. |

**Portas ajustadas por conflito no ambiente:**
- Banco: `5434:5432` (5432/5433 já usados por outros projetos).
- API: `8109:8000` (8000 usado por outro projeto). A porta local do `main.py` já era 8109.

---

## 7. `.env` (local) e `.env.exemplo`

### 7.1. `.env` corrigido
- **Typo removido:** `.../mangas_livros@@` → `.../mangas_livros` (o `@@` virava parte do nome do banco).
- **Host:** `localhost:5434` (porta mapeada do compose) — antes apontava para `db:5432`, que só existe dentro da rede Docker.
- **Vars novas adicionadas:** `ENVIRONMENT=development`, `SSL_MODE=disable`, `ALGORITHM=HS256`, `REFRESH_TOKEN_EXPIRE_MINUTES`, cookies e cloudinary (vazios/desativados).

### 7.2. `.env.exemplo`
- Atualizado para refletir a porta `5434` e o formato de produção com `?sslmode=require`.

---

## 8. Ambiente — venv recriado em Python 3.11.8

### 8.1. Problema encontrado (herdado da Sprint 0)
- O `.venv` estava em **Python 3.14** (sem `pip` e sem nenhum pacote), enquanto o projeto mira **3.11.8** (`.python-version` e `Dockerfile`).

### 8.2. Solução aplicada
1. Instalei `uv` (gerenciador de Python) via instalador oficial → `~/.local/bin/uv`.
2. `uv python install 3.11.8` → baixou um CPython 3.11.8 standalone.
3. `uv venv --python 3.11.8 .venv` → recriou o venv na versão correta.
4. `uv pip install -r requirements.txt` → instalou todas as dependências (58 pacotes).
5. `httpx` **adicionado ao `requirements.txt`** (`httpx==0.28.1` + `httpcore==1.0.9`) — necessário para o `TestClient` do FastAPI/pytest.

> ⚠️ Se o `uv` não estiver disponível na sua máquina: `pip install uv` também instala.
> A partir de agora, `source .venv/bin/activate` dá um ambiente **Python 3.11.8** funcional.

---

## 9. Validações realizadas (com resultados)

| Validação | Comando | Resultado |
|---|---|---|
| Config + conexão local | `python -c "from app.database.conexao import engine; ..."` | ✅ Conexão OK (porta 5434) |
| App importa sem create_all | `python -c "import app.main"` | ✅ 31 rotas, sem criar tabelas |
| Migração baseline | `alembic upgrade head` | ✅ 6 tabelas + `alembic_version` |
| Sem drift | `alembic check` | ✅ "No new upgrade operations detected" |
| Reversibilidade | `alembic downgrade base` + `upgrade head` | ✅ tabelas removidas e recriadas |
| App em Docker | `docker compose up -d api` + curl | ✅ `/docs` e `/mangas/` → 200 |
| Fluxo auth completo | TestClient e curl | ✅ register 200, login 200, token emitido |
| Testes existentes | `pytest -q` | 2 passed, 5 errors (ver seção 10) |

---

## 10. Estado dos testes (baseline)

```
2 passed, 2 warnings, 5 errors
```

- `test_register` e `test_login` **passam** (auth funciona com a nova config).
- 5 erros: todos `KeyError: 'access_token'` no `conftest.py` — a fixture `auth_token`
  depende de um usuário fixo `hidan@gmail.com / hidan` que **não existe** no banco local.
  Isso é o problema conhecido de isolamento de testes (Sprint 6). **Não é regressão** desta sprint.

---

## 11. Problemas encontrados e resolvidos

| Problema | Solução |
|---|---|
| Venv em Python 3.14 sem pip | `uv` instalou Python 3.11.8 e recriou o venv |
| `ensurepip` ausente no Python do uv | Usei `uv venv` (que não depende de ensurepip) |
| Porta 5432/5433 ocupadas por outros projetos | Banco deste projeto mapeado para **5434** |
| Porta 8000 ocupada | API mapeada para **8109** |
| `httpx` ausente (TestClient quebrado) | Adicionado `httpx==0.28.1` + `httpcore==1.0.9` ao requirements |
| `.env` com `@@` e host `db` | Corrigido para `localhost:5434`; compose sobrescreve para `db:5432` |

---

## 12. Como usar (fluxo de desenvolvimento)

```bash
# Subir banco + API (Docker)
docker compose up -d db api

# Aplicar migrações (se o banco estiver vazio)
docker compose run --rm api alembic upgrade head
#   ou, localmente:
alembic upgrade head

# Rodar a API localmente (sem Docker)
source .venv/bin/activate
uvicorn app.main:app --reload

# Parar tudo
docker compose down
```

---

## 13. Achados anotados para sprints futuras

1. **`.venv/` e `__pycache__/` estão versionados no git** (commitados no passado; `.gitignore` só vale para arquivos novos). Recomendação de higiene: `git rm -r --cached .venv` e `git rm -r --cached **/__pycache__` + commit (fora do escopo desta sprint, pois não foi solicitado commit).
2. **`criar_tabelas.py`** ainda importa `criacao` (inexistente) — será corrigido/removido na Sprint 3.
3. **Sprint 2** usará `ALGORITHM`, `COOKIE_*` e o fluxo de refresh/rotação já configurados aqui.
4. **Sprint 3** adicionará UniqueConstraints, FKs `nullable=False`, `ondelete=CASCADE`, colunas `criado_em/atualizado_em` e a tabela `refresh_tokens` via novas migrações Alembic.
5. **Produção (Supabase):** rodar `alembic stamp head` na primeira vez (banco já tem as tabelas via `create_all` antigo) e, a partir daí, `alembic upgrade head` para cada mudança.

---

## 14. Próximos passos (Sprint 2 — Autenticação e JWT)

- Consolidar auth em 1 arquivo (`core/dependecia_auth.py`); remover duplicata `utils/dependecias_utils.py`.
- Corrigir `jwt_gerenciador.py` (`create_refresh_token` duplicado, `expirar_em`→`expirar_na`, usar `config.ALGORITHM`).
- Criar tabela `refresh_tokens` + rotas `/auth/refresh` (rotação/revogação) e `/auth/logout`.
- Cookies HttpOnly + Secure + SameSite (login/refresh/logout).
- Registro com `role="user"` (remover hardcode `admin`) + `seed_admin.py`.
- Rate limiting no login.