# 🗄️ Sprint 3 — Modelagem e migração do banco

> Documento detalhado do que foi feito na Sprint 3.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md) (seção 3)
> Sprint anterior: [`SPRINT_2.md`](SPRINT_2.md)

---

## 1. Objetivo da Sprint 3

Aplicar no banco as correções de modelagem identificadas na análise (seção 3 do plano),
via **Alembic**, sem perder dados:

- UniqueConstraints para evitar duplicidade;
- FKs `nullable=False` + `ondelete=CASCADE`;
- colunas de timestamp (`criado_em`/`atualizado_em`) e `usuarios.ativo`;
- dropar a coluna duplicada `livros.capa_livro`;
- remover `criar_tabelas.py` (Alembic é a única fonte de schema).

---

## 2. Mudanças nos models

### 2.1. `usuarios` — `criado_em` e `ativo`

```python
criado_em = Column(DateTime, server_default=func.now(), nullable=False)
ativo     = Column(Boolean, nullable=False, default=True, server_default="true")
```

- `ativo` prepara bloqueio de usuário (fase micro-SaaS). `server_default="true"`
  garante que linhas existentes ganhem `true` na migração.

### 2.2. `mangas` — timestamps

```python
criado_em   = Column(DateTime, server_default=func.now(), nullable=False)
atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

- `onupdate=func.now()` atualiza automaticamente no UPDATE (SQLAlchemy).

### 2.3. `manga_volumes` — unique + cascade

```python
__table_args__ = (
    UniqueConstraint("manga_id", "numero", name="uq_manga_volumes_manga_numero"),
)
manga_id = Column(Integer, ForeignKey("mangas.id", ondelete="CASCADE"), nullable=False)
```

- Impede dois volumes com o mesmo número para o mesmo mangá.
- FK `ON DELETE CASCADE`: apagar o mangá apaga os volumes.

### 2.4. `livros` — remoção de duplicada

- **Removida:** `capa_livro` (duplicava `capa_url`).
- **Adicionada:** `atualizado_em` (mesma convenção das demais).

### 2.5. `usuarios_favoritos_livros` e `usuarios_favoritos_mangas` — unique + cascade

```python
__table_args__ = (
    UniqueConstraint("usuario_id", "livro_id", name="uq_favorito_livro_usuario_livro"),
)
usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
livro_id   = Column(Integer, ForeignKey("livros.id", ondelete="CASCADE"), nullable=False)
```

- Usuário não pode favoritar o mesmo item duas vezes.
- FKs `nullable=False` + `ON DELETE CASCADE`: remover usuário/item limpa os favoritos
  (o controller deixou de precisar gerenciar isso — e de quebrar com FK).

---

## 3. Migração Alembic

```
alembic revision --autogenerate -m "sprint3 constraints cascades timestamps capa"
```

### 3.1. `alembic/versions/96cef16a19bf_sprint3_constraints_cascades_timestamps_.py`

Upgrade:
1. `livros`: + `atualizado_em`, **drop** `capa_livro`
2. `manga_volumes`: unique `uq_manga_volumes_manga_numero`; FK recriada com `ondelete='CASCADE'`
3. `mangas`: + `criado_em`, `atualizado_em`
4. `usuarios`: + `criado_em`, `ativo`
5. Favoritos: `alter_column nullable=False`, unique constraints, FKs recriadas com `ondelete='CASCADE'`

### 3.2. Correção manual importante (autogenerate)
O autogenerate criou as FKs com `create_foreign_key(None, ...)`. **Ajuste necessário:**
nomes explícitos no padrão Postgres `{tabela}_{coluna}_fkey` para o **downgrade**
(`drop_constraint`) funcionar. Sem isso, o downgrade quebraria com `None`.

```python
op.create_foreign_key(op.f('manga_volumes_manga_id_fkey'), 'manga_volumes',
                      'mangas', ['manga_id'], ['id'], ondelete='CASCADE')
```

### 3.3. Reversibilidade validada
`alembic downgrade -1` → `alembic upgrade head` OK (round-trip sem erro).

---

## 4. Verificação do schema final

Consultando `pg_constraint` + `information_schema` após `upgrade head`:

| Constraint | Tipo | Definição |
|---|---|---|
| `uq_manga_volumes_manga_numero` | UNIQUE | `(manga_id, numero)` |
| `uq_favorito_livro_usuario_livro` | UNIQUE | `(usuario_id, livro_id)` |
| `uq_favorito_manga_usuario_manga` | UNIQUE | `(usuario_id, manga_id)` |
| `manga_volumes_manga_id_fkey` | FK | `ON DELETE CASCADE` |
| `usuarios_favoritos_livros_livro_id_fkey` | FK | `ON DELETE CASCADE` |
| `usuarios_favoritos_livros_usuario_id_fkey` | FK | `ON DELETE CASCADE` |
| `usuarios_favoritos_mangas_manga_id_fkey` | FK | `ON DELETE CASCADE` |
| `usuarios_favoritos_mangas_usuario_id_fkey` | FK | `ON DELETE CASCADE` |

Colunas: `mangas.criado_em/atualizado_em`, `usuarios.criado_em/ativo`,
`livros.atualizado_em` (`nullable=NO`); `livros.capa_livro` removida.

`alembic check` → **"No new upgrade operations detected"** (0 drift).

---

## 5. Validação de CASCADE (teste real)

1. **Admin** cria mangá → **admin** adiciona volume (`POST /mangas/{id}/volumes/`) ✅ 201
2. **User** favorita (`POST /favoritos/manga/{manga_id}`) ✅ 200
3. **Admin** deleta o mangá ✅ 200
4. Resultado no banco: `manga_volumes = 0`, `usuarios_favoritos_mangas = 0` ✅

> Antes (sem CASCADE), `deletar` precisava apagar volumes/favoritos manualmente no
> controller e ainda podia quebrar por FK. Agora o banco cuida disso.

---

## 6. `criar_tabelas.py` removido

- O script rodava `Base.metadata.create_all` — **fora** do Alembic.
- Com migrações em vigor, o schema é 100% controlado por `alembic upgrade head`
  (decisão Sprint 1). Nenhuma referência ao script restou no código.

---

## 7. Estado dos testes

`pytest`: **2 passed, 5 errors** — mesma baseline (erros do conftest que depende de
`hidan@gmail.com`; correção na Sprint 6). Sem regressão introduzida pela Sprint 3.

---

## 8. Achados para sprints futuras

1. **Sprint 4** — caminhos de favoritos são singulares (`/favoritos/manga/{id}`),
   sem prefixo `/favoritos/mangas/`. Organização/unificação de rotas fica para lá.
2. **Sprint 6** — os testes de favoritos/volumes precisarão de fixture com admin
   (hoje erram por falta de `access_token` no conftest).
3. `usuario_controller.py` e `criar_tabelas` não são mais necessários no fluxo
   principal; decisão de remoção na Sprint 4.

---

## 9. Arquivos tocados

```
app/models/livros_model.py           -capa_livro, +atualizado_em
app/models/manga_model.py            +criado_em, atualizado_em
app/models/manga_volume_model.py     +UniqueConstraint, FK ondelete=CASCADE
app/models/usuario_model.py          +criado_em, ativo
app/models/favoritos_model.py        +UniqueConstraints, FKs nullable=False+ondelete=CASCADE
alembic/versions/96cef16a19bf_sprint3_constraints_cascades_timestamps_.py   nova migração
criar_tabelas.py                     REMOVIDO
PLANO_DE_MELHORIAS.md                Sprint 3 marcada
```

---

## 10. Próximos passos (Sprint 4 — Correção de bugs em schemas/controllers/rotas)

- `MangaUpdate` (remover `volumes`/`descricao`), `MangaCreate` completo,
  `MangaResponse`/`LivroResponse` sincronizados com os models.
- Corrigir/remover `usuario_controller.py`; `LivroController.deletar` simplificado
  (CASCADE já cuida dos favoritos); response models em todos os endpoints.
- Limpeza: `svhemas_favoritos.py`, `routa_favoritos_livros`, `app/teste.py`,
  rota `/teste-admin`, import duplicado em `rotas_autentica.py`.
- `comprado` de volume passa a body (`VolumeUpdate`), não query param.