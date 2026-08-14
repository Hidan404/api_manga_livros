# ✅ Sprint 6 — Testes, CI e qualidade

> Documento detalhado do que foi feito na Sprint 6.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Sprint anterior: [`SPRINT_5.md`](SPRINT_5.md)

---

## 1. Objetivo da Sprint 6

- Testes **confiáveis e isolados** (sem depender de `hidan@gmail.com` nem do banco real);
- cobrir os fluxos principais (auth, CRUD, favoritos, upload);
- CI automatizada + lint/format;
- endpoint `/health` + logging estruturado.

---

## 2. Testes isolados — `tests/conftest.py` (reescrito)

### 2.1. Banco isolado (SQLite)

Antes de importar o app, o conftest define as variáveis de ambiente (pydantic-settings lê
env com precedência sobre o `.env`):

```python
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///./tests/test_api.db"
os.environ["SSL_MODE"] = "disable"
os.environ["CLOUDINARY_URL"] = ""
```

- O banco `tests/test_api.db` é **criado na sessão** (`create_all`) e **destruído no fim**.
- Entre testes, todas as tabelas são **zeradas** (fixture `_limpar_tabelas` autouse) → isolamento.
- FKs do SQLite: `PRAGMA foreign_keys=ON` via `event.listens_for(engine, "connect")` —
  sem isso, `ON DELETE CASCADE` não é aplicado no SQLite.
- `tests/test_api.db` adicionado ao `.gitignore`.

### 2.2. Compatibilidade do app com SQLite

Dois ajustes no código de produção (também mais robustos em geral):

1. **`app/database/conexao.py`**: `connect_args={"sslmode": ...}` agora é aplicado **apenas
   para URLs PostgreSQL** (SQLite não aceita `sslmode` no connect).
2. **`app/controllers/autenticar_controller.py`**: ao verificar a expiração do refresh,
   `expira_em` é normalizado para tz-aware quando vier naive (SQLite devolve naive;
   Postgres devolve com timezone) antes de comparar com `datetime.now(UTC)`.

### 2.3. Fixtures

| Fixture | Função |
|---|---|
| `client` | `TestClient` com `get_db` sobrescrito para a sessão de teste |
| `admin_credenciais` | cria admin direto no banco (`role=admin`) e retorna email/senha |
| `admin_headers` | faz **login de verdade** via API e retorna `Authorization: Bearer` |
| `user_headers` | register + login de usuário comum |

> O rate limit (`limiter.enabled = False`) é desativado nos testes: o slowapi conta por IP
> e o TestClient usa sempre o mesmo endereço → "10/minute" estouraria rápido.

---

## 3. Cobertura de testes (34 testes)

```
tests/test_auth.py       10  register (ok/duplicado), login (ok/errado/cookies),
                              rota via cookie, refresh rotação + reuso, logout,
                              somente admin cria
tests/test_mangas.py      6  user 403, admin cria completo, listar/obter,
                              atualizar com sinopse, deletar
tests/test_livros.py      6  user 403, admin cria (isbn/sinopse), listar,
                              atualizar, deletar
tests/test_volumes.py     6  adicionar (comprado no body), duplicado 400,
                              atualizar via body, listar ordenado, remover
tests/test_favoritos.py   6  adicionar (com titulo), duplicado 400, 404,
                              listar, remover, CASCADE ao deletar mangá
tests/test_upload.py      4  requer admin 403, tipo inválido 400,
                              extensão inválida 400, sem Cloudinary 503
tests/test_health.py      1  /health 200 com banco ok
```

**Resultado:** `34 passed` (antes: 2 passed, 5 errors dependendo do banco real).

---

## 4. `/health` + logging estruturado

### 4.1. `GET /health`
Adicionado em `app/main.py`:
```python
@app.get("/health")
def health():
    banco = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        banco = "indisponível"
    return {"status": "ok", "versao": app.version, "banco": banco}
```
Resposta local: `{"status": "ok", "versao": "1.0.0", "banco": "ok"}`.

### 4.2. `app/core/logging_config.py` (novo)
- `configurar_logging()` chamado no import do `app.main`.
- **Produção**: formato **JSON** (`ts`, `nivel`, `logger`, `msg`) — pronto para agregar no Render.
- **Desenvolvimento**: formato texto legível.
- Idempotente (não duplica handlers em reload).

---

## 5. Lint/format — ruff

### 5.1. `ruff.toml` (novo)
```toml
target-version = "py311"
line-length = 100
exclude = [".venv", "alembic/versions", "tests/test_api.db"]

[lint]
select = ["E", "F", "W", "I", "B", "UP"]
ignore = ["B008", "E501"]
```

- `B008` ignorado: `Depends(...)`/`File(...)` como default é o padrão do FastAPI.
- `alembic/versions` excluído: migrações são autogeradas.

### 5.2. Correções aplicadas (`ruff check --fix` + manuais)
- `Optional[X]` → `X | None` (UP007/UP045/UP035) em schemas, routers, models, controllers.
- Ordenação de imports (`I001`).
- `class RoleUsuario(str, Enum)` → `enum.StrEnum` (UP042) — valor continua serializando
  como string.
- `raise HTTPException(...) from None` em except (B904): `rota_registro.py`,
  `dependecia_auth.py`.

**Resultado:** `ruff check .` → `All checks passed!`

---

## 6. CI — `.github/workflows/ci.yml` (novo)

```yaml
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

- Roda **lint + testes** em cada push/PR — sem banco externo (testes usam SQLite).
- `pytest==9.0.2` e `ruff==0.12.2` já constam no `requirements.txt`.

---

## 7. Validações realizadas

| Etapa | Resultado |
|---|---|
| `pytest -q` | ✅ 34 passed (antes 2 passed / 5 errors) |
| `ruff check .` | ✅ All checks passed |
| Docker rebuild + `GET /health` | ✅ `{"status":"ok","versao":"1.0.0","banco":"ok"}` |
| `GET /mangas/` no Docker | ✅ 200 |

---

## 8. Arquivos tocados

```
tests/conftest.py                       reescrito (SQLite isolado + fixtures)
tests/test_auth.py, test_mangas.py,
test_livros.py, test_volumes.py,
test_favoritos.py, test_upload.py,
test_health.py                          reescritos/novos
app/database/conexao.py                 sslmode só p/ postgres (compat SQLite)
app/controllers/autenticar_controller.py expira_em naive → tz-aware
app/main.py                             + /health, configurar_logging()
app/core/logging_config.py              NOVO
app/core/roles.py                       StrEnum (UP042)
app/routers/rota_registro.py            raise ... from None
app/core/dependecia_auth.py             raise ... from None
ruff.toml                               NOVO
.github/workflows/ci.yml                NOVO
requirements.txt                        + ruff
.gitignore                              + tests/test_api.db
app/schemas/*, app/routers/*, app/models/*   typing modernizado (ruff --fix)
PLANO_DE_MELHORIAS.md                   Sprint 6 marcada
```

---

## 9. Achados / observações

1. **`app/teste.py`** foi removido na Sprint 4; a execução de teste isolado não depende
   mais de nenhum banco real.
2. O **rate limit desativado em teste** é intencional; em CI a app de teste não sobe em
   produção.
3. O banco de teste é recriado por sessão — rodar `pytest` não toca no banco de dev.

---

## 10. Próximo passo (Sprint 7 — Deploy Render + Supabase documentado)

- Revisar/atualizar `docs/ROTEIRO_DEPLOY.md` com tudo que mudou (Sprints 1–6);
- Procedimento de rotação de secrets;
- Checklist de verificação pós-deploy;
- Reproduzir o deploy seguindo só o doc.