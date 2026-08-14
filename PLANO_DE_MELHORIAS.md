# 📋 Plano de Melhorias — API Manga Livros

> Documento de consulta para desenvolvedor e assistente. Atualizar a cada sprint concluída.
> Data de criação: 2026-08-14

---

## 1. Contexto

API REST FastAPI (Python 3.11) em camadas (Routers → Controllers → Models), PostgreSQL, JWT.

- **Deploy atual:** Render (API) + Supabase (banco)
- **Estado:** exige correções críticas de runtime, segurança e organização
- **Objetivo:** base estável, segura e extensível para evoluir para um micro-SaaS

> ⚠️ O procedimento do deploy atual e as secrets foram perdidos. Serão documentados com
> **placeholders** em `docs/ROTEIRO_DEPLOY.md`. Nenhum valor real entra no repositório.

---

## 2. Decisões confirmadas

| # | Tema | Decisão |
|---|------|---------|
| 1 | Capas/upload | Serviço externo (**Cloudinary** por padrão; trocável por S3/B2) |
| 2 | Refresh tokens | Tabela `refresh_tokens` com revogação + rotação |
| 3 | Migrações | **Alembic** substitui `Base.metadata.create_all` |
| 4 | Deploy/secrets | Roteiro documentado com placeholders; nenhum secret real no repo |
| 5 | Roles | Manter `user`/`admin` (string) por enquanto; design **extensível** para micro-SaaS |
| 6 | Token no frontend | Cookies **HttpOnly + Secure + SameSite** (login/refresh/logout) |

---

## 3. Análise da lógica das tabelas (verificação realizada)

### 3.1. Modelos atuais

| Tabela | Problema encontrado | Correção planejada |
|---|---|---|
| `usuarios` | Base ok (email unique, role default "user") | + `criado_em`, `ativo` (bool, p/ bloqueio) |
| `mangas` | Sem `criado_em`/`atualizado_em` (schemas exigem) | + colunas `DateTime` |
| `manga_volumes` | Sem `UniqueConstraint(manga_id, numero)`; FK nullable | Unique + `nullable=False` + `ondelete=CASCADE` |
| `livros` | Colunas duplicadas `capa_url` **e** `capa_livro` | Dropar `capa_livro`; manter `capa_url` + `atualizado_em` |
| `usuarios_favoritos_livros` | Sem Unique em `(usuario_id, livro_id)`; FK nullable; sem cascade | Unique + `nullable=False` + `ondelete=CASCADE` |
| `usuarios_favoritos_mangas` | Sem Unique em `(usuario_id, manga_id)`; FK nullable; sem cascade | Unique + `nullable=False` + `ondelete=CASCADE` |
| `refresh_tokens` | **Não existe** (jti gerado, nunca persistido) | Criar: `jti` unique, `usuario_id`, `expira_em`, `revogado`, `criado_em` |

### 3.2. Notas de lógica

- Deleção de mangá já limpa favoritos no controller; com `ondelete=CASCADE` no banco, fica robusto e o `LivroController.deletar` deixa de quebrar por FK.
- `capa_url` será padronizado em todos os modelos (URL do serviço externo).

---

## 4. Roles — design extensível (fase micro-SaaS)

### Decisão
`role` continua string no banco (`user`, `admin`). Não criar tabela de roles agora.

### Implementação
- Criar `app/core/roles.py` com enum/constantes:
  ```python
  class RoleUsuario(str, enum.Enum):
      ADMIN = "admin"
      USER  = "user"
  ```
- Model `Usuario.role` usa o enum; schemas e `require_role` leem o mesmo registro.
- Adicionar `require_any_role("admin", "editor", ...)` para quando surgirem novas roles.
- **Adicionar uma role nova = alterar 1 arquivo** (`app/core/roles.py`).

### Fora de escopo (anotado como "fase micro-SaaS")
- Permissões granulares por recurso → evoluir para tabela `roles`/`permissoes` (RBAC) **sem quebrar** a estrutura atual.
- O design com enum central + `require_any_role` não bloqueia essa evolução futura.

---

## 5. Entrega segura do token ao frontend (HttpOnly Cookies)

### 5.1. Problema
Login hoje devolve `{"access_token": ...}` no corpo. O frontend precisaria guardar em
`localStorage`, que é legível por qualquer script injetado (**XSS** — principal vetor de
ataque em SPAs). Um script malicioso faz `localStorage.getItem("token")` e exfiltra o token.

### 5.2. Por que cookies HttpOnly é seguro

| Flag/estratégia | Efeito | Defende contra |
|---|---|---|
| `HttpOnly` | `document.cookie` **não enxerga** o cookie; só o navegador envia | XSS (token não é legível/copiável por JS) |
| `Secure` | Cookie só trafega via HTTPS | Interceptação de rede (MITM) |
| `SameSite=Lax/Strict` | Cookie **não é enviado** em requisições cross-site | CSRF |
| Access token curto (~15 min) | Janela de exposição mínima | Replay/uso indevido |
| Refresh com **rotação** | Uso gera novo token; antigo revogado no banco | Roubo de refresh (reuso detectável) |

**Resumo:** o frontend **nunca toca no token** — o navegador guarda e envia sozinho.
Mesmo com XSS, não há token para roubar. Remove o maior vetor de roubo de token em SPA.

### 5.3. Como será implementado (Sprint 2)

1. **Login** (`POST /auth/login`): valida credenciais → gera access + refresh → define cookies na resposta:
   - `access_token`: `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900` (15 min)
   - `refresh_token`: `HttpOnly; Secure; SameSite=Strict; Path=/auth; Max-Age=30d` (só enviado à rota de refresh — superfície menor)
2. **Frontend**: `fetch(url, { credentials: "include" })`; não guarda nada. Em `401`, chama
   silenciosamente `POST /auth/refresh` (cookie enviado sozinho) e repete a requisição.
3. **Refresh com rotação**: `/auth/refresh` valida o cookie de refresh, **revoga o jti usado**
   (tabela `refresh_tokens`), emite novo e reescreve os cookies. Reuso do mesmo cookie =
   sinal de roubo → revoga a sessão inteira.
4. **Logout** (`POST /auth/logout`): revoga o refresh no banco e limpa os cookies.
5. **Auth nas rotas**: `get_current_user` passa a aceitar o access cookie (mantendo
   compatibilidade com `Authorization: Bearer` durante a transição), validando `token_type=access`.
6. **CORS**: `allow_credentials=True` (já existe) + origem explícita do frontend (sem wildcard).
7. **Config por ambiente**: `COOKIE_SECURE=true` em produção (HTTPS), `false` no localhost;
   `COOKIE_SAMESITE` e `COOKIE_DOMAIN` via env.
8. **Docs**: seção no `docs/ROTEIRO_DEPLOY.md` com exemplo de consumo pelo frontend.

### 5.4. Trade-off anotado
Cookies HttpOnly exigem HTTPS em produção (Render já fornece) e atenção ao CORS. Em troca,
eliminam o maior vetor de roubo de token. Alternativa futura (não adotada agora): access em
memória + refresh em HttpOnly — mais robusta, porém mais complexa; anotada como evolução.

---

## 6. Sprints

### Sprint 0 — Documentação e baseline
**Objetivo:** registrar o estado atual e o roteiro de deploy em um único lugar de consulta.

- [ ] Criar `PLANO_DE_MELHORIAS.md` (este arquivo) e `docs/ROTEIRO_DEPLOY.md`
- [ ] Inventário de variáveis de ambiente usadas no código
- [ ] Reescrever `.env.exemplo` completo (todas as vars, com placeholders)
- [ ] Criar `app/core/roles.py` (enum de roles)

**Aceite:** consulta documentada em 1 lugar; `.env.exemplo` bate com o código.

---

### Sprint 1 — Configuração e conexão com o banco
**Objetivo:** app inicia sem crash e sem side-effects no import.

- [ ] `configuracao.py`: adicionar `ALGORITHM`, `ENVIRONMENT`, SSL configurável
- [ ] Remover defaults fracos de secret (`SECRET_KEY="Ronald123"`, `REFRESH_SECRET_KEY`) — falhar em produção se ausente
- [ ] `conexao.py`: `sslmode` via env (Supabase exige `require`; local não) — remover hardcode
- [ ] Corrigir `.env` (typo `@@`, host `db` vs `localhost`)
- [ ] **Alembic:** `alembic init`, migração baseline do schema atual
- [ ] Remover `Base.metadata.create_all` do import em `main.py`
- [ ] Healthcheck + `depends_on: condition: service_healthy` no docker-compose

**Aceite:** `alembic upgrade head` cria o banco; app inicia sem conexão no import.

---

### Sprint 2 — Autenticação e JWT (corrigir, consolidar e cookies)
**Objetivo:** auth única, segura, com refresh/rotação e tokens entregues via HttpOnly.

- [ ] **Consolidar auth em 1 lugar:** manter `core/dependecia_auth.py`, remover duplicata `utils/dependecias_utils.py`
- [ ] `get_current_user` valida `token_type=access` (rejeitar refresh como access); role vinda **do banco** (não de email)
- [ ] Corrigir `jwt_gerenciador.py`: remover `create_refresh_token` duplicado; `expirar_em`→`expirar_na`; usar `config.ALGORITHM`; chave separada p/ refresh
- [ ] Criar model + tabela `refresh_tokens`; rotas `/auth/refresh` (rotação + revogação) e `/auth/logout`
- [ ] Implementar cookies HttpOnly + Secure + SameSite conforme seção 5.3
- [ ] Login retorna access + refresh (cookies); schema `Token` ajustado
- [ ] Registro: `role="user"` por padrão (remover hardcode `admin`); criar `seed_admin.py`
- [ ] Rate limiting no login (slowapi)

**Aceite:** register→login→refresh→logout testado; refresh revogado é rejeitado; reuso de refresh detectado; só admin cria conteúdo.

---

### Sprint 3 — Modelagem e migração do banco
**Objetivo:** aplicar as correções da seção 3 via Alembic, sem perder dados em produção.

- [ ] Migrações: UniqueConstraints, FKs `nullable=False`, `ondelete=CASCADE`, colunas novas
- [ ] Dropar `livros.capa_livro`; padronizar `capa_url`
- [ ] Criar tabela `refresh_tokens`
- [ ] Corrigir `criar_tabelas.py` (importar `engine`) ou removê-lo (Alembic substitui)

**Aceite:** `alembic upgrade head` aplica no Supabase de produção sem perder dados; índices únicos funcionando.

---

### Sprint 4 — Correção de bugs em schemas/controllers/rotas
**Objetivo:** alinhar schemas/models e eliminar dead code.

- [ ] `MangaUpdate`: remover `volumes`/`descricao`; usar `sinopse`
- [ ] `MangaCreate` completo (`artista`, `data_lancamento`, `capa_url`)
- [ ] `MangaResponse`/`LivroResponse` sincronizados com os models
- [ ] Corrigir `usuario_controller.py` (dead code quebrado) ou removê-lo
- [ ] `LivroController.deletar`: tratar favoritos (via CASCADE do banco)
- [ ] Response models em todos os endpoints (sem ORM puro)
- [ ] Limpeza: typo `svhemas_favoritos.py`, `routa_favoritos_livros`, import duplicado em `rotas_autentica.py`, remover `app/teste.py` e rota `/teste-admin`
- [ ] `comprado` de volume passa a body (`VolumeUpdate`), não query param

**Aceite:** PUT de mangá com `sinopse` funciona; deletar livro favoritado não quebra; `/docs` sem endpoints de teste.

---

### Sprint 5 — Upload de capas (Cloudinary)
**Objetivo:** imagens fora do Postgres; apenas URLs gravadas no banco.

- [ ] Config `CLOUDINARY_URL` + SDK; uploads salvam no Cloudinary e gravam a **URL** em `capa_url`/`capa_volume`
- [ ] Validação: tamanho máximo (ex.: 5MB), content-type e extensões permitidas
- [ ] Corrigir leitura binária em colunas `String` (bug atual)

**Aceite:** upload de capa retorna URL acessível; arquivo inválido retorna 400.

---

### Sprint 6 — Testes, CI e qualidade
**Objetivo:** testes confiáveis e pipeline automatizada.

- [ ] Refatorar testes: banco isolado (fixture); remover dependência de `hidan@gmail.com`
- [ ] Fixture cria usuário admin
- [ ] Cobrir: auth (cookies, refresh, revogação), CRUD mangas/livros/volumes, favoritos, upload
- [ ] CI GitHub Actions rodando `pytest` a cada push
- [ ] Lint/format com `ruff`
- [ ] Endpoint `/health` + logging estruturado

**Aceite:** `pytest` verde em ambiente limpo; CI passando.

---

### Sprint 7 — Deploy Render + Supabase (documentado)
**Objetivo:** reproduzir o deploy seguindo só o doc (sem dados reais no repo).

- [ ] `docs/ROTEIRO_DEPLOY.md` completo (ver seção 7)
- [ ] Roteiro de rotação de secrets
- [ ] Checklist de verificação pós-deploy

**Aceite:** qualquer pessoa reproduz o deploy só seguindo o doc.

---

## 7. Roteiro de Deploy — resumo

Detalhado em `docs/ROTEIRO_DEPLOY.md`. Resumo:

- **Supabase:** criar projeto → connection string (pooler + SSL) → `DATABASE_URL` de produção
- **Render:** criar Web Service → build/start command → **env vars no dashboard** (não no repo) → publicar
- **Migrações:** `alembic upgrade head` contra produção; **backup antes de cada migração**
- **Rotação de secrets:** trocar `SECRET_KEY`/`REFRESH_SECRET_KEY` sem derrubar sessões (procedimento documentado)
- **Verificação:** login, refresh, logout, CRUD, favoritos, upload, `/health`

---

## 8. Mapa de arquivos afetados

```
app/core/configuracao.py          Sprint 1
app/core/dependecia_auth.py       Sprint 2
app/core/roles.py                 Sprint 0 (novo)
app/database/conexao.py           Sprint 1
app/main.py                       Sprint 1, 4
app/utils/jwt_gerenciador.py      Sprint 2
app/utils/dependecias_utils.py    Sprint 2 (remover)
app/models/*                      Sprint 2, 3
app/schemas/*                     Sprint 4
app/controllers/*                 Sprint 4, 5
app/routers/*                     Sprint 2, 4
tests/*                           Sprint 6
criar_tabelas.py                  Sprint 3
.env.exemplo                      Sprint 0
docker-compose.yml                Sprint 1
seed_admin.py                     Sprint 2 (novo)
alembic/                          Sprint 1 (novo)
app/models/refresh_token_model.py Sprint 2 (novo)
docs/ROTEIRO_DEPLOY.md            Sprint 0 (novo)
.github/workflows/ci.yml          Sprint 6 (novo)
```

---

## 9. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Banco de produção tem dados reais | Migrações **incrementais e reversíveis**; backup antes de cada `upgrade head` |
| Secrets do deploy perdidos | Recuperação só via dashboard Render/Supabase; processo documentado (não recuperável pelo assistente) |
| Cloudinary free tier | Limite de storage suficiente para estudo; trocável por S3/B2 sem mudar schema |
| Quebra de sessões na troca de auth (Bearer→cookie) | Transição mantém compatibilidade com `Authorization: Bearer` (Sprint 2) |
| XSS/roubo de token | Cookies HttpOnly + Secure + SameSite; refresh com rotação e revogação |

---

## 10. Histórico de decisões

| Data | Decisão |
|---|---|
| 2026-08-14 | Capas → Cloudinary; refresh → tabela `refresh_tokens`; migrações → Alembic; deploy → doc com placeholders |
| 2026-08-14 | Roles mantidas `user`/`admin` (extensível); token → HttpOnly cookies com rotação |