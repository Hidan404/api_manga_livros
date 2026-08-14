# 🔐 Sprint 2 — Autenticação e JWT (consolidar, corrigir e cookies)

> Documento detalhado do que foi feito na Sprint 2.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Sprint anterior: [`SPRINT_1.md`](SPRINT_1.md)

---

## 1. Objetivo da Sprint 2

Autenticação **única, corrigida e segura**:
- corrigir o JWT/refresh (que estava quebrado);
- consolidar em 1 arquivo (remover duplicata);
- entregar o token ao frontend via **cookies HttpOnly**;
- refresh com **rotação e revogação** (detecção de reuso);
- registro com `role=user` por padrão + script de seed de admin;
- rate limiting no login.

### Entregas planejadas
| Entrega | Status |
|---|---|
| `jwt_gerenciador.py` corrigido (duplicação, `expirar_em`, `ALGORITHM`, chave separada) | ✅ |
| Tabela `refresh_tokens` + model | ✅ |
| Auth consolidada em `core/dependecia_auth.py` (token_type, role do banco, header+cookie) | ✅ |
| `utils/dependecias_utils.py` removida | ✅ |
| `AuthController` com cookies HttpOnly + rotação/revogação | ✅ |
| Rotas `/auth/refresh` e `/auth/logout` | ✅ |
| Registro com `role=user` + `seed_admin.py` | ✅ |
| Rate limiting no login (slowapi) | ✅ |
| Migração Alembic `add refresh_tokens table` | ✅ |

---

## 2. `app/utils/jwt_gerenciador.py` — JWT corrigido

### 2.1. O que estava quebrado
1. `create_refresh_token` era definido **DUAS vezes** — a 2ª sobrescrevia a 1ª e usava
   `config.ALGORITHM` e `self.expirar_em()` que **não existiam** → `AttributeError`.
2. `verificar_refresh_token` usava `config.ALGORITHM` (inexistente) → o refresh nunca funcionava.
3. Access e refresh usavam a **mesma chave**.

### 2.2. Código corrigido (pontos-chave)

```python
def __init__(self):
    self.ALGORITMO = config.ALGORITHM          # agora lido da config (Sprint 1)
    self.SECRET = config.SECRET_KEY            # chave dos ACCESS tokens
    self.REFRESH_SECRET = config.REFRESH_SECRET_KEY  # chave dos REFRESH tokens

def create_refresh_token(self, user_id, expires_days=None):
    expire = self.expirar_na(dias=expires_days or config.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = secrets.token_hex(16)                # id único persistido no banco
    payload = self.base_payload(user_id, {
        "type": "refresh",
        "exp": int(expire.timestamp()),
        "jti": jti,
    })
    return jwt.encode(payload, self.REFRESH_SECRET, algorithm=self.ALGORITMO)

def decode_token(self, token, secret=None):
    secret = secret or self.SECRET
    return jwt.decode(token, secret, algorithms=[self.ALGORITMO])
```

| Mudança | Por quê |
|---|---|
| `expirar_em` → `expirar_na` | nome do método existente; corrige `AttributeError` |
| `self.REFRESH_SECRET` separado | refresh não é assinado com a mesma chave do access |
| `decode_token(token, secret=None)` | permite decodificar refresh com a chave de refresh |
| `decode_access_token` / `decode_refresh_token` | helpers que já escolhem a chave certa |
| 1 única `create_refresh_token` | elimina a sobrescrita acidental |

---

## 3. Tabela e model `refresh_tokens`

### 3.1. Model `app/models/refresh_token_model.py`

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    expira_em = Column(DateTime(timezone=True), nullable=False)
    revogado = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime(timezone=True), nullable=False,
                       default=lambda: datetime.now(UTC))

    usuario = relationship("Usuario", back_populates="refresh_tokens")
```

### 3.2. Por que persistir o refresh token?
| Necessidade | Como a tabela resolve |
|---|---|
| **Logout** | apaga/revoga a linha do `jti` |
| **Rotação** | o `jti` usado é marcado `revogado=True` ao emitir um novo |
| **Detecção de reuso** | se um `jti` já revogado for usado de novo → possível roubo → revoga a sessão inteira |

### 3.3. `app/models/__init__.py` (novo)
Importa todos os models. Importar o pacote `app.models` registra **tudo** na `Base.metadata`
e no registry de relacionamentos — corrige o erro de scripts standalone
(`InvalidRequestError: ... failed to locate a name 'UsuarioFavoritoLivro'`).

### 3.4. `Usuario` atualizado
- `role` default passa a ser `RoleUsuario.USER.value` (registro central de roles).
- novo relacionamento `refresh_tokens` com `cascade="all, delete-orphan"`.

### 3.5. Migração Alembic
```
alembic revision --autogenerate -m "add refresh_tokens table"
alembic upgrade head
```
Resultado: tabela `refresh_tokens` criada (FK para `usuarios.id`, `jti` unique com índice).

---

## 4. Auth consolidada — `app/core/dependecia_auth.py`

### 4.1. Única fonte de autenticação
`app/utils/dependecias_utils.py` foi **removida**. Agora só existe
`core/dependecia_auth.py`. Todos os routers foram atualizados para importar daqui:
`rotas_livros`, `rotas_mangas`, `rotas_favoritos_mangas`, `rotas_favoritos_livros`.

### 4.2. `get_current_user` (header OU cookie)

```python
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(request: Request, token: str = Depends(oauth2)):
    if not token:
        token = request.cookies.get("access_token")   # fallback: cookie HttpOnly
    if not token:
        raise HTTPException(401, "Não autenticado...")
    try:
        payload = jwt_manager.decode_access_token(token)
    except JWTError:
        raise HTTPException(401, "Token inválido ou expirado")
    if not jwt_manager.is_token_type(payload, "access"):
        raise HTTPException(401, "Token não é do tipo access")
    ...
    # role vem do BANCO:
    return {"id": user.id, "email": user.email, "role": user.role}
```

| Mudança | Detalhe |
|---|---|
| `auto_error=False` | sem header → não levanta 401 automaticamente; permite cair no cookie |
| `request.cookies.get("access_token")` | aceita token do cookie HttpOnly (transição para cookies) |
| `decode_access_token` | usa a chave de access e valida assinatura/expirado |
| `is_token_type(payload, "access")` | **rejeita** refresh token usado como access |
| role do banco | antes era derivada de `email.endswith("@admin.com")` — removido |

### 4.3. `require_role` e `require_any_role`

```python
def require_role(role):            # require_role(RoleUsuario.ADMIN)
    expected = _normalizar_role(role)
    if expected not in ROLES_VALIDAS:
        raise ValueError(...)
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != expected:
            raise HTTPException(403, "Acesso negado")
        return user
    return role_checker

def require_any_role(*roles):      # require_any_role("admin", "editor")
    allowed = {_normalizar_role(r) for r in roles}
    ...
```

- `_normalizar_role` aceita `"admin"` (string) **ou** `RoleUsuario.ADMIN` (enum).
- Valida contra `ROLES_VALIDAS` (registro central) → erro claro se a role não existir.
- `require_any_role` é a preparação para novas roles (fase micro-SaaS).

---

## 5. `AuthController` — cookies e rotação

### 5.1. Cookies definidos (PLANO seção 5)

| Cookie | Atributos |
|---|---|
| `access_token` | `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900` (15 min) |
| `refresh_token` | `HttpOnly; Secure; SameSite=Strict; Path=/auth; Max-Age=30d` |

```python
def _definir_cookies(self, response, access_token, refresh_token):
    response.set_cookie("access_token", access_token,
        httponly=True, secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60, path="/")
    response.set_cookie("refresh_token", refresh_token,
        httponly=True, secure=config.COOKIE_SECURE,
        samesite="strict",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600, path="/auth")
```

| Atributo | Efeito |
|---|---|
| `httponly=True` | JS não lê via `document.cookie` → protege contra XSS |
| `secure=config.COOKIE_SECURE` | só HTTPS em produção (Render) |
| `samesite="strict"` (refresh) | nunca enviado em requests cross-site → anti-CSRF |
| `path="/auth"` (refresh) | o refresh só viaja para `/auth/*` (menor superfície) |

### 5.2. `login`
1. Valida credenciais (`SenhaHasher.verificar_senha`).
2. Emite access (com `role`) + refresh (com `jti`).
3. Persiste o `jti` na tabela `refresh_tokens`.
4. Define os cookies.
5. Retorna os tokens no corpo **e** cookies (transição; o frontend deve usar os cookies).

### 5.3. `refresh_token` — ROTAÇÃO

```python
stored = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

if not stored or stored.revogado:
    if stored:
        self._revogar_todos(db, user_id)     # reuso = possível roubo
    raise HTTPException(401, "Sessão comprometida. Faça login novamente.")

if stored.expira_em < datetime.now(UTC):
    raise HTTPException(401, "Refresh token expirado")

stored.revogado = True                        # ROTAÇÃO: revoga o atual
db.commit()
... # emite novo par e persiste o novo jti
```

**Fluxo de segurança:** cada uso do refresh emite um novo; o antigo é revogado. Se um
token antigo for reenviado (roubo), a sessão inteira do usuário é invalidada.

### 5.4. `logout`
- Revoga (deleta) o refresh token do cookie/corpo no banco.
- Limpa os cookies (`delete_cookie` para `Path=/` e `Path=/auth`).

---

## 6. Rotas `/auth`

```python
@rota.post("/login",  response_model=Token, ...)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginSchema, response: Response, db=Depends(get_db)):
    return auth_controller.login(db, payload.email, payload.senha, response)

@rota.post("/refresh", response_model=Token, ...)
def refresh_token(request, response, payload: Optional[RefreshTokenSchema] = None, db=Depends(get_db)):
    token = request.cookies.get("refresh_token") or (payload.refresh_token if payload else None)
    ...
    return auth_controller.refresh_token(db, token, response)

@rota.post("/logout", ...)
def logout(request, response, db=Depends(get_db)):
    return auth_controller.logout(db, request.cookies.get("refresh_token"), response)
```

- **refresh**: lê o cookie primeiro (Path=/auth é enviado automaticamente), corpo como fallback.
- **Schema `Token`** agora inclui `refresh_token` e `role` (ver `autentica_schemas.py`).

---

## 7. Registro com `role=user` + `seed_admin.py`

### 7.1. `rota_registro.py`
```python
novo_usuario = Usuario(..., role=RoleUsuario.USER.value)
```
O registro **nunca confia** em role vinda do cliente (antes era `role="admin"` hardcoded —
falha de segurança crítica). Admin é criado **apenas** via seed.

### 7.2. `seed_admin.py` (novo)
```python
load_dotenv()   # lê ADMIN_EMAIL/ADMIN_SENHA do .env
def criar_admin():
    ...
    if usuario:
        usuario.role = RoleUsuario.ADMIN.value   # promove
    else:
        db.add(Usuario(..., role=RoleUsuario.ADMIN.value))  # cria
```
Uso: `python seed_admin.py` (vars do `.env`). Adicionadas `ADMIN_EMAIL`/`ADMIN_SENHA`
no `.env` e `.env.exemplo`.

---

## 8. Rate limiting (slowapi)

### 8.1. `app/core/rate_limit.py` (novo)
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### 8.2. `app/main.py`
```python
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 8.3. Uso
`@limiter.limit("10/minute")` na rota de login (10 tentativas por IP por minuto).

| Item | Detalhe |
|---|---|
| Lib | `slowapi==0.1.10` (adicionado ao `requirements.txt` junto com `wrapt`) |
| Chave | IP de origem (`get_remote_address`) |
| Storage | memória por processo (OK para 1 worker no Render; Redis para multi-worker) |
| Endpoint protegido | login (brute force) |

---

## 9. Migrações e arquivos

### 9.1. Migração nova
`alembic/versions/9adbf8f1dfa7_add_refresh_tokens_table.py` (upgrade cria `refresh_tokens`).

### 9.2. Arquivos tocados
```
app/utils/jwt_gerenciador.py        reescrito
app/models/refresh_token_model.py   novo
app/models/__init__.py              novo (registro central de models)
app/models/usuario_model.py         role default + refresh_tokens
app/core/dependecia_auth.py         reescrito (consolidado)
app/core/rate_limit.py              novo
app/utils/dependecias_utils.py      REMOVIDO
app/controllers/autenticar_controller.py  reescrito
app/schemas/autentica_schemas.py    Token com refresh_token/role
app/routers/rotas_autentica.py      login/refresh/logout + cookies + rate limit
app/routers/rota_registro.py        role=user
app/routers/rotas_livros.py         imports auth
app/routers/rotas_mangas.py         imports auth
app/routers/rotas_favoritos_*.py    imports auth
app/main.py                         limiter
alembic/env.py                      import refresh_token_model
seed_admin.py                       novo
requirements.txt                    + slowapi, wrapt
.env / .env.exemplo                 + ADMIN_EMAIL, ADMIN_SENHA
```

---

## 10. Validações realizadas

| Etapa | Resultado |
|---|---|
| Register → role=user | ✅ 200 |
| Login → tokens + cookies (`access_token`, `refresh_token`) | ✅ 200, cookies `HttpOnly` |
| Rota protegida via **header Bearer** | ✅ 200 |
| Rota protegida via **cookie** (sem header) | ✅ 200 |
| Refresh via cookie (rotação) | ✅ 200, novo par emitido |
| **Reuso** de refresh antigo (sem cookie) | ✅ 401 "Sessão comprometida" |
| Logout (limpa cookies + revoga) | ✅ 200, cookies zerados |
| Criar manga com role=user | ✅ 403 (acesso negado) |
| Seed admin + criar manga com admin | ✅ 201 |
| Docker (rebuild com slowapi) + cookies no HTTP real | ✅ `Set-Cookie` com `HttpOnly; Path=/auth; SameSite=strict` |
| `pytest` | 2 passed, 5 errors (conftest `hidan@gmail.com` — Sprint 6) |

---

## 11. Como o frontend deve consumir (resumo)

```javascript
// Login (cookie é definido automaticamente)
await fetch(".../auth/login", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, senha }),
});

// Requisição autenticada (cookie access_token viaja sozinho)
await fetch(".../mangas/", { credentials: "include" });

// Em 401 → refresh silencioso (cookie refresh_token viaja só para /auth)
await fetch(".../auth/refresh", { method: "POST", credentials: "include" });

// Logout
await fetch(".../auth/logout", { method: "POST", credentials: "include" });
```

> Detalhe em [`ROTEIRO_DEPLOY.md`](ROTEIRO_DEPLOY.md) seção 6.

---

## 12. Achados para sprints futuras

1. **Testes (Sprint 6):** conftest ainda depende de `hidan@gmail.com` — os 5 erros de
   `pytest` são isso; o fluxo real está validado (seção 10).
2. **`/mangas/teste-admin`** ainda existe (Sprint 4 o remove).
3. **Sprint 3** adiciona UniqueConstraints, FKs `nullable=False`, cascade e colunas
   `criado_em/atualizado_em` (inclusive na tabela `refresh_tokens` recém-criada).
4. **Slowapi** em memória: se a app rodar com múltiplos workers no Render, o contador
   de rate limit é por processo (documentado no módulo).

---

## 13. Próximos passos (Sprint 3 — Modelagem e migração do banco)

- UniqueConstraints (`manga_id+numero`, `usuario_id+livro_id/manga_id`).
- FKs `nullable=False` + `ondelete=CASCADE` (favoritos, volumes).
- Colunas `criado_em`/`atualizado_em` em `mangas`/`livros`/`usuarios`; dropar `livros.capa_livro`.
- Corrigir/remover `criar_tabelas.py`.