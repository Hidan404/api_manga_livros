# 🧱 Sprint 0 — Documentação e Baseline

> Documento detalhado do que foi feito na Sprint 0.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Roteiro de deploy: [`ROTEIRO_DEPLOY.md`](ROTEIRO_DEPLOY.md)

---

## 1. Objetivo da Sprint 0

Registrar o estado atual do projeto e preparar a base de consulta, sem alterar o
comportamento da aplicação. Nenhuma mudança funcional — apenas **documentação** e
**criação do registro central de roles** (arquivo novo, sem impacto no código existente).

### Entregas planejadas
| Entrega | Status |
|---|---|
| `PLANO_DE_MELHORIAS.md` (plano geral) | ✅ já criado |
| `docs/ROTEIRO_DEPLOY.md` (deploy Render + Supabase) | ✅ já criado |
| Inventário de variáveis de ambiente usadas no código | ✅ feito nesta sprint |
| `.env.exemplo` reescrito (completo, com placeholders) | ✅ feito nesta sprint |
| `app/core/roles.py` (enum de roles extensível) | ✅ feito nesta sprint |
| `docs/SPRINT_0.md` (este documento) | ✅ feito nesta sprint |

---

## 2. Inventário de variáveis de ambiente

### 2.1. Como foi feito
Busquei no código todas as ocorrências de `os.getenv()`, `os.environ` e acesso a
`config.<ATRIBUTO>` (via `grep`), e cruzei com o conteúdo do `.env` atual e do
`.env.exemplo` antigo.

### 2.2. Tabela completa

| Variável | Onde é usada hoje | Default atual no código | Problema encontrado |
|---|---|---|---|
| `DATABASE_URL` | `app/database/conexao.py` (`os.getenv`) e `app/core/configuracao.py` | `None` | `.env` atual tem typo `@@` no final; host `db` só funciona dentro do Docker |
| `SECRET_KEY` | `app/core/configuracao.py` → `app/utils/jwt_gerenciador.py` | `"Ronald123"` ⚠️ | Default fraco e hardcoded |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `app/core/configuracao.py` | `60` | OK, mas 60 min é longo p/ access |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `app/core/configuracao.py` | `7` | OK |
| `REFRESH_SECRET_KEY` | `app/core/configuracao.py` | `"chave_refresh_secreta"` ⚠️ | Default fraco e hardcoded |
| `ALGORITHM` | **NENHUM** — presente no `.env` mas não é lido | — | `config` não tem atributo `ALGORITHM`; código usa `ALGORITMO` hardcoded na classe JWT → quebra o refresh (Sprint 2) |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | **NENHUM** — valor hardcoded `43200` no `configuracao.py` | `43200` | Não é configurável via env |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Apenas `docker-compose.yml` (criação do container) | — | OK, não são usadas pelo app |
| `SSL_MODE` | **NENHUM** (não existe) | — | Necessária: hoje `sslmode=require` está hardcoded em `conexao.py` (Sprint 1) |
| `ENVIRONMENT` | **NENHUM** (não existe) | — | Necessária: distinguir prod/dev para validar secrets e cookies (Sprints 1–2) |
| `COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_DOMAIN` | **NENHUM** (não existem) | — | Necessárias para entrega de token via HttpOnly cookies (Sprint 2) |
| `CLOUDINARY_URL` | **NENHUM** (não existe) | — | Necessária para upload de capas via serviço externo (Sprint 5) |

### 2.3. Conclusão do inventário
O código lê hoje **5 variáveis** de verdade (`DATABASE_URL`, `SECRET_KEY`,
`ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `REFRESH_SECRET_KEY`).
O `.env.exemplo` antigo declarava 2 que não são lidas (`ALGORITHM`, e os `POSTGRES_*`),
e **faltavam 6** que o plano exige (`ENVIRONMENT`, `SSL_MODE`, `COOKIE_*`, `CLOUDINARY_URL`).
Tudo isso foi incorporado ao novo `.env.exemplo`.

---

## 3. `.env.exemplo` reescrito

### 3.1. O que mudou
- Organizado por **seções** com comentários (`Ambiente`, `JWT`, `Cookies`, `PostgreSQL`, `Cloudinary`, `Database`).
- Adicionadas as 6 variáveis novas previstas no plano.
- Documentado o comando para gerar chaves seguras (`secrets.token_hex(32)`).
- Documentados os 2 formatos de `DATABASE_URL` (local sem SSL / Supabase com `?sslmode=require`).
- **Corrigido** o typo `@@` do final da URL (que estava no `.env` atual).

### 3.2. Conteúdo completo

```ini
# ============================================================
# API Manga Livros — Exemplo de variáveis de ambiente
#
# COMO USAR:
#   1. Copie este arquivo para `.env`
#      (cp .env.exemplo .env)
#   2. Preencha com valores reais
#   3. O `.env` está no .gitignore e NUNCA deve ir para o repo
#
# GERE CHAVES SEGURAS COM:
#   python -c "import secrets; print(secrets.token_hex(32))"
# ============================================================

# ---------------- Ambiente ----------------
ENVIRONMENT=development

# ---------------- JWT ----------------
SECRET_KEY=your_super_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# ---------------- Cookies (Sprint 2) ----------------
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
COOKIE_DOMAIN=

# ---------------- PostgreSQL ----------------
POSTGRES_DB=mangas_livros
POSTGRES_USER=usuario
POSTGRES_PASSWORD=sua_senha_aqui

# ---------------- Cloudinary (Sprint 5) ----------------
CLOUDINARY_URL=cloudinary://seu_api_key:seu_api_secret@sua_cloud_name

# ---------------- Database Connection URL ----------------
DATABASE_URL=postgresql+psycopg://usuario:sua_senha_aqui@localhost:5432/mangas_livros

# ---------------- SSL ----------------
SSL_MODE=disable
```

### 3.3. Sintaxe do formato `.ini`/`.env`
- Linhas no formato `CHAVE=valor`.
- Comentários iniciam com `#`.
- Valores não precisam de aspas (a menos que contenham `#` ou espaços).
- O `python-dotenv` (lib `dotenv`) carrega esse arquivo via `load_dotenv()` — usado em
  `app/core/configuracao.py` e `app/database/conexao.py`.

---

## 4. `app/core/roles.py` — registro central de roles

### 4.1. Código completo

```python
"""Registro central de roles da aplicação (Sprint 0)."""

from enum import Enum
from typing import Set


class RoleUsuario(str, Enum):
    """Roles válidas no sistema."""

    ADMIN = "admin"
    USER = "user"


ROLES_VALIDAS: Set[str] = {role.value for role in RoleUsuario}
```

### 4.2. Lógica e sintaxe explicadas

| Elemento | Explicação |
|---|---|
| `from enum import Enum` | Lib da **stdlib** (sem dependência externa). Fornece a base para criar enums. |
| `class RoleUsuario(str, Enum)` | Enum que **herda de `str`**. Por isso o valor `"admin"` é usado como string pura em tudo (banco, JWT, Pydantic), em vez do nome do membro `RoleUsuario.ADMIN`. Sem `str`, `str(RoleUsuario.ADMIN)` retornaria `"RoleUsuario.ADMIN"`. |
| `ADMIN = "admin"` / `USER = "user"` | Membros do enum. O valor fica do lado direito; o nome do membro do lado esquerdo. |
| `ROLES_VALIDAS: Set[str] = {role.value for role in RoleUsuario}` | Set derivado automaticamente do enum (compreensão de conjunto). Se você adicionar `EDITOR = "editor"` no enum, `ROLES_VALIDAS` ganha `"editor"` **sem editar este set** — uma única fonte de verdade. |

### 4.3. Por que extensível (fase micro-SaaS)
Para criar uma nova role (ex.: `EDITOR`), basta adicionar uma linha ao enum:
```python
class RoleUsuario(str, Enum):
    ADMIN = "admin"
    USER  = "user"
    EDITOR = "editor"   # nova role em 1 linha
```
`ROLES_VALIDAS` se ajusta sozinho. As validações (schemas, `require_role`,
`require_any_role` — Sprint 2) passarão a ler deste único arquivo.

### 4.4. Uso previsto nas próximas sprints
```python
# Model (Sprint 2/3) — default vindo do enum
from app.core.roles import RoleUsuario
role = Column(String(50), nullable=False, default=RoleUsuario.USER.value)

# Controle de acesso (Sprint 2) — comparando com .value
if usuario.role != RoleUsuario.ADMIN.value:
    raise HTTPException(status_code=403, detail="Acesso negado")
```

### 4.5. Libs usadas
- `enum` — **stdlib**, já instalada. Nenhuma dependência nova foi adicionada.

---

## 5. Estrutura de arquivos (criados nesta sprint)

```
api_manga_livros/
├── PLANO_DE_MELHORIAS.md          # plano geral (já existia)
├── .env.exemplo                   # REESCRITO — inventário completo com placeholders
├── app/
│   └── core/
│       └── roles.py               # NOVO — enum de roles + ROLES_VALIDAS
└── docs/
    ├── ROTEIRO_DEPLOY.md          # roteiro Render + Supabase (já existia)
    └── SPRINT_0.md                # este documento
```

---

## 6. Como validar

```bash
# 1. O módulo de roles importa sem erro e expõe os valores esperados
cd /home/hidan/Documentos/api_manga_livros
source .venv/bin/activate
python -c "
from app.core.roles import RoleUsuario, ROLES_VALIDAS
print(RoleUsuario.ADMIN.value)     # admin
print(RoleUsuario.USER.value)      # user
print(ROLES_VALIDAS)               # {'admin', 'user'}
print(RoleUsuario.ADMIN)           # RoleUsuario.ADMIN
"

# 2. Copiar o exemplo para .env local (sobrescreve o atual com valores placeholder)
cp .env.exemplo .env

# 3. Validar que o .env.exemplo é lido corretamente pelo python-dotenv
python -c "from dotenv import dotenv_values; v = dotenv_values('.env.exemplo'); print(f'{len([k for k in v if not k.startswith(chr(35))])} variáveis OK')"
```

> ⚠️ A Sprint 0 **não altera** `configuracao.py`, `conexao.py` nem o `main.py` —
> isso é a Sprint 1. O `.env` recém-copiado tem placeholders; rode apenas os comandos
> de validação acima, sem subir a API, para não quebrar a conexão com o banco ainda.

---

## 7. Achados de ambiente (baseline)

Durante a validação, descobri problemas no ambiente virtual local que impedem o app de rodar:

| Achado | Detalhe | Ação |
|---|---|---|
| **Venv sem pacotes** | `pip list` retornava vazio; nem `pip` existia no venv (`ModuleNotFoundError: No module named 'pip'`) | Executado `python -m ensurepip --upgrade` — restaurou o pip |
| **Venv em Python 3.14** | O venv aponta para o Python 3.14 do sistema (`site-packages/...python3.14`), mas `.python-version` define **3.11.8** e o `Dockerfile` usa `python:3.11` | **Divergência a corrigir** — idealmente recriar o venv com Python 3.11 (Sprint 1) |
| **Só Python 3.14 disponível** | `python3.11`, `3.12` e `3.10` não existem no sistema; sem `pyenv` | Instalar 3.11 (via pyenv/apt) ou documentar uso do Docker para dev |
| **`requirements.txt` completo não instalado** | Instalação total falhou pois o venv não tinha pip; alguns pins podem não ter wheel p/ 3.14 | Avaliar instalação no Sprint 1; deploy Render usa `python:3.11` |
| **`python-dotenv` ausente** | `from dotenv import load_dotenv` (usado em `configuracao.py`/`conexao.py`) falharia — venv não tinha o pacote | Instalado `python-dotenv` apenas para validar o `.env.exemplo` |
| **`.gitignore` ignorava os planos** | `PLANO_DE_MELHORIAS.md` e `docs/ROTEIRO_DEPLOY.md` haviam sido adicionados ao `.gitignore` — os arquivos de consulta nunca seriam versionados | Removidas essas 2 linhas do `.gitignore` |
| **`.venv/bin/*` versionado** | Scripts do venv (`.venv/bin/pip`, `activate`, etc.) foram commitados no passado — `.venv` só passa a ser ignorado para arquivos **novos** | Recomendação (fora de escopo): `git rm -r --cached .venv` num sprint de higiene |

**Conclusão:** o ambiente local atual **não executa a API**. Isso não bloqueia a Sprint 0
(documentação + `roles.py`, que usa apenas a stdlib), mas deve ser resolvido na Sprint 1
para o app voltar a rodar localmente.

---

## 8. Decisões registradas

1. **Enum com `str, Enum`** (e não `StrEnum` do 3.11): compatível com Python 3.10+
   (README afirma suporte 3.10+), mesmo o `.python-version` sendo 3.11.8.
2. **`ROLES_VALIDAS` derivado do enum** em vez de uma lista manual: evita dessincronização.
3. **`.env.exemplo` com todas as vars do plano**, mesmo as de sprints futuras
   (Cookies, Cloudinary, SSL_MODE): o exemplo já serve de guia único do que configurar.

---

## 9. Próximos passos (Sprint 1 — Configuração e conexão com o banco)

- `configuracao.py`: ler `ALGORITHM`, `ENVIRONMENT`, `SSL_MODE`; remover defaults fracos de secret.
- `conexao.py`: usar `SSL_MODE` (remover `sslmode=require` hardcoded).
- Alembic: `alembic init` + migração baseline; remover `create_all` do import em `main.py`.
- Healthcheck no `docker-compose.yml`.
- **Ambiente:** recriar o venv em Python 3.11 (corrigir divergência 3.14 → 3.11) e instalar o `requirements.txt` completo.