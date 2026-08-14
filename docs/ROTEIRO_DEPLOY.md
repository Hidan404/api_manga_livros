# 🚀 Roteiro de Deploy — API Manga Livros (Render + Supabase)

> Documento de consulta para reproduzir o deploy. **Não colocar valores reais aqui** —
> use os placeholders `<...>` e preencha no dashboard dos provedores.
> Associado a: `PLANO_DE_MELHORIAS.md` (Sprint 7).

---

## 1. Visão geral da arquitetura

```
[Frontend (SPA)]  --HTTPS-->  [Render: API FastAPI (uvicorn)]  --SSL-->  [Supabase: PostgreSQL]
```

- **Render** hospeda a API (Web Service, Python, `uvicorn`).
- **Supabase** hospeda o PostgreSQL (exige SSL → `sslmode=require`).
- Secrets ficam como **variáveis de ambiente no dashboard do Render**, nunca no repo.

---

## 2. Variáveis de ambiente (inventário)

> Preencher no Render (Environment → Env Groups). Valores de exemplo entre `< >`.

| Variável | Uso | Exemplo |
|---|---|---|
| `DATABASE_URL` | Conexão com o Postgres do Supabase | `postgresql+psycopg://<user>:<pass>@<host>:<port>/<db>?sslmode=require` |
| `SECRET_KEY` | Assinatura dos access tokens (JWT) | `<hex-aleatorio-32-bytes>` |
| `REFRESH_SECRET_KEY` | Assinatura dos refresh tokens (JWT) | `<hex-aleatorio-32-bytes-diferente>` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do access token | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Validade do refresh token | `30` |
| `COOKIE_SECURE` | `true` em produção (HTTPS) | `true` |
| `COOKIE_SAMESITE` | Política SameSite dos cookies | `lax` |
| `COOKIE_DOMAIN` | Domínio do cookie (opcional) | `<seu-dominio>` |
| `CLOUDINARY_URL` | Credenciais do Cloudinary | `cloudinary://<key>:<secret>@<cloud>` |
| `ENVIRONMENT` | `production` / `development` | `production` |
| `ADMIN_EMAIL` | Email do admin (seed_admin.py) | `admin@seudominio.com` |
| `ADMIN_SENHA` | Senha do admin (seed_admin.py) | `<senha-forte>` |

> As variáveis `POSTGRES_DB/USER/PASSWORD` são usadas **só pelo docker-compose local**;
> não são necessárias no Render.

**Gerar chaves seguras:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Supabase (banco)

1. Criar projeto em https://supabase.com
2. Ir em **Project Settings → Database → Connection string**
3. Usar a **connection string de produção (pooler ou direta)** com `sslmode=require`
4. Formato esperado pela app:
   ```
   postgresql+psycopg://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>?sslmode=require
   ```
   - Driver: `postgresql+psycopg` (psycopg v3)
   - `sslmode=require` é **obrigatório** no Supabase
5. Guardar esse valor para colar no Render (env `DATABASE_URL`)

> ⚠️ NUNCA commitar a connection string real no repositório.

---

## 4. Render (API)

1. Criar **Web Service** apontando para o repositório `https://github.com/Hidan404/api_manga_livros`
2. Configuração:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     > Render injeta a porta via `$PORT` — não fixar 8000.
3. Em **Environment**, criar env group com todas as variáveis da seção 2 (valores reais aqui)
4. Deploy automático em push para `main` (ou manual)
5. Confirmar que a app sobe: acessar `https://<app>.onrender.com/health`
6. **Criar o admin** (uma vez, após o deploy + migrações):
   ```bash
   # No Render, via Shell de uma instância ou execução one-off:
   python seed_admin.py
   # Lê ADMIN_EMAIL/ADMIN_SENHA das variáveis de ambiente do Render.
   ```
   Resultado: cria o usuário admin (`role=admin`) ou promove se já existir.

---

## 5. Migrações de banco (Alembic)

> Executar **antes de publicar código novo** que dependa de schema novo.

### 5.1. Local (desenvolvimento)
```bash
alembic upgrade head
```

### 5.2. Produção (Supabase)
1. **Fazer backup** do banco antes (ver seção 7)
2. Gerar/confirmar a migração:
   ```bash
   alembic revision --autogenerate -m "descricao"
   ```
3. Rodar contra produção:
   ```bash
   DATABASE_URL="<connection-string-real>" alembic upgrade head
   ```

### 5.3. Rollback (se necessário)
```bash
alembic downgrade -1
```
> Sempre verificar se a migração é reversível antes de aplicar em produção.

> A cadeia de migrações (head) cobre: schema baseline, tabela `refresh_tokens`
> e a Sprint 3 (unique constraints, FKs `nullable=False` + `ON DELETE CASCADE`,
> `criado_em`/`atualizado_em`, `usuarios.ativo`, remoção de `livros.capa_livro`).
> Depois do upgrade, confirmar com `alembic check` (0 drift).

---

## 5.5. Cloudinary (upload de capas — Sprint 5)

Imagens não ficam no Postgres: a API envia o arquivo ao Cloudinary e grava apenas a
**URL** em `capa_url` / `capa_volume`.

### 5.5.1. Criar a conta
1. Criar conta em https://cloudinary.com (plano free suficiente para estudo)
2. No dashboard, copiar a URL da conta (API Environment variable):
   ```
   cloudinary://<api_key>:<api_secret>@<cloud_name>
   ```
3. Colar em `CLOUDINARY_URL` no env do Render (seção 2)

### 5.5.2. Como a API usa
- `app/core/capa_upload.py` configura o SDK a partir de `CLOUDINARY_URL` e valida o arquivo:
  - **tamanho** máximo 5MB;
  - **content-type**: `image/jpeg`, `image/png`, `image/webp`, `image/gif`;
  - **extensão**: `jpg/jpeg/png/webp/gif`.
- Endpoints (admin):
  - `POST /mangas/{manga_id}/upload-capa`
  - `POST /mangas/{manga_id}/volumes/{numero}/upload-capa`
  - `POST /livros/{livro_id}/upload-capa`
- Resposta: `{"mensagem": ..., "capa_url": "https://res.cloudinary.com/..."}`

### 5.5.3. Erros possíveis
| Caso | Status |
|---|---|
| Arquivo inválido (tipo/extensão/tamanho) | `400` |
| `CLOUDINARY_URL` ausente | `503` (upload não configurado) |
| Falha no serviço do Cloudinary | `502` |

---

## 6. Configuração do frontend (cookies HttpOnly)

O token é entregue via **cookie HttpOnly** — o frontend nunca armazena token.

```javascript
// Login
const res = await fetch("https://<app>.onrender.com/auth/login", {
  method: "POST",
  credentials: "include", // envia/recebe cookies
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, senha }),
});

// Requisição autenticada
const res2 = await fetch("https://<app>.onrender.com/mangas/", {
  credentials: "include",
});

// Em 401: refresh silencioso e repete a requisição
async function fetchAutenticado(url, opts = {}) {
  let res = await fetch(url, { ...opts, credentials: "include" });
  if (res.status === 401) {
    await fetch("https://<app>.onrender.com/auth/refresh", { method: "POST", credentials: "include" });
    res = await fetch(url, { ...opts, credentials: "include" });
  }
  return res;
}

// Logout
await fetch("https://<app>.onrender.com/auth/logout", {
  method: "POST",
  credentials: "include",
});
```

**Requisitos:**
- O frontend precisa estar em um domínio/porta na lista de origens do CORS (`allow_origins`)
- Em produção, `COOKIE_SECURE=true` (HTTPS obrigatório)

---

## 7. Backup e recuperação

### Backup do banco (Supabase)
- Dashboard → **Database → Backups** (backups automáticos diários do Supabase)
- Para backup manual, exportar via `pg_dump`:
  ```bash
  pg_dump "<connection-string-real>" > backup_$(date +%F).sql
  ```

### Recuperação de secrets
- Secrets estão no dashboard do Render (env group) e do Supabase
- Se perder a `SECRET_KEY`: **rodar migração que invalide os refresh tokens**
  (revogar todos `jti` na tabela `refresh_tokens`) para forçar novo login

---

## 8. Rotação de secrets (sem derrubar todos os logins)

1. Adicionar `SECRET_KEY_NOVA` no Render
2. O código passa a assinar com a nova chave **mas continua validando a antiga**
   (lista de chaves válidas por um período de transição)
3. Após o período (ex.: 2x a validade do access token), remover `SECRET_KEY` antiga
4. Revogar refresh tokens antigos na tabela `refresh_tokens`

---

## 9. Checklist de verificação pós-deploy

- [ ] `GET /health` retorna 200 com `banco: ok`
- [ ] `POST /auth/register` cria usuário com `role=user`
- [ ] `POST /auth/login` seta cookies `access_token` e `refresh_token` (HttpOnly)
- [ ] `GET /mangas/` autenticado funciona (cookie enviado)
- [ ] `POST /auth/refresh` renova o access cookie e revoga o anterior
- [ ] Reuso do mesmo refresh cookie é **rejeitado** (rotação)
- [ ] `POST /auth/logout` limpa cookies e revoga o refresh
- [ ] `seed_admin.py` criou o admin (`role=admin`) usando `ADMIN_EMAIL`/`ADMIN_SENHA`
- [ ] Somente admin consegue criar/editar/deletar mangás e livros
- [ ] CRUD de volumes e favoritos funcionando
- [ ] Upload de capa retorna URL pública do Cloudinary; arquivo inválido → 400
- [ ] CORS: frontend real (origem explícita) funciona com `credentials: "include"`
- [ ] `alembic upgrade head` aplicado; `alembic check` sem drift; índices únicos ativos
