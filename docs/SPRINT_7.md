# 🚀 Sprint 7 — Deploy Render + Supabase (documentado)

> Documento resumo da Sprint 7.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Sprint anterior: [`SPRINT_6.md`](SPRINT_6.md)

---

## 1. Objetivo

O roteiro em [`ROTEIRO_DEPLOY.md`](ROTEIRO_DEPLOY.md) deve permitir reproduzir o deploy
**sem nenhum dado real no repositório** (secrets recuperáveis só nos dashboards).

---

## 2. O que foi atualizado em `docs/ROTEIRO_DEPLOY.md`

### 2.1. Variáveis de ambiente (seção 2)
- + `ADMIN_EMAIL` e `ADMIN_SENHA` (usadas pelo `seed_admin.py`).
- Nota: `POSTGRES_DB/USER/PASSWORD` são apenas do docker-compose local — não vão ao Render.

### 2.2. Render (seção 4)
- Passo novo: **executar `python seed_admin.py`** após deploy + migrações (cria/promove o
  admin a partir das vars `ADMIN_EMAIL`/`ADMIN_SENHA` do env do Render).

### 2.3. Migrações (seção 5)
- Nota do que a cadeia de migrações (head) cobre:
  baseline → `refresh_tokens` → Sprint 3 (constraints, cascades, timestamps, `capa_livro` drop).
- Recomendação: `alembic check` após o upgrade (0 drift).

### 2.4. Checklist pós-deploy (seção 9)
- `banco: ok` no `/health`;
- seed admin verificado;
- upload: arquivo inválido → 400;
- `alembic check` sem drift.

> As seções de **rotação de secrets (8)** e **backup/recuperação (7)** já existiam e foram
> mantidas.

---

## 3. Estado final do projeto (Sprints 0–7)

| Área | Resultado |
|---|---|
| Config/ambiente | pydantic-settings, secrets validados em produção, SSL configurável, venv 3.11 via uv |
| Banco | Alembic (3 migrações), constraints únicas, FKs `nullable=False` + CASCADE, timestamps |
| Auth | JWT corrigido, cookies HttpOnly, refresh com rotação/revogação, rate limit no login |
| Upload | Cloudinary com validação (5MB/tipo/extensão), URL no banco |
| Código | schemas sincronizados, response models, dead code removido, tipografia corrigida |
| Qualidade | 34 testes verdes (SQLite isolado), ruff limpo, CI GitHub Actions, `/health` + logs JSON |
| Deploy | `docs/ROTEIRO_DEPLOY.md` completo (placeholders, backup, rotação de secrets, checklist) |

---

## 4. Validação final

- `pytest -q` → **34 passed**
- `ruff check .` → **All checks passed**
- `alembic check` → **0 drift**
- Docker: `GET /health` → `{"status":"ok","versao":"1.0.0","banco":"ok"}`
- CI: `.github/workflows/ci.yml` pronto (lint + testes a cada push/PR)

---

## 5. Pendências anotadas (fora do escopo atual)

1. **Secrets reais** do Render/Supabase/Cloudinary: só recuperáveis nos dashboards —
   preencher os placeholders do ROTEIRO manualmente.
2. **Upload real** testado com credencial Cloudinary de verdade (fluxo 503 → 200) quando
   a `CLOUDINARY_URL` existir.
3. Evolução futura: RBAC com tabela de roles/permissoes (micro-SaaS) — o design atual
   (`roles.py` + `require_any_role`) não bloqueia isso.