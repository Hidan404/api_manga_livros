# 🐛 Sprint 4 — Correção de bugs em schemas/controllers/rotas

> Documento detalhado do que foi feito na Sprint 4.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md)
> Sprint anterior: [`SPRINT_3.md`](SPRINT_3.md)

---

## 1. Objetivo da Sprint 4

- Alinhar **schemas ↔ models** (campos certos, sem `descricao`/`volumes` fantasma);
- **Response models** em todos os endpoints (sem devolver ORM puro);
- `comprado` de volume passa a **body** (`VolumeUpdate`), não query param;
- Eliminar dead code e typos;
- Simplificar deleção (o CASCADE do banco — Sprint 3 — cuida dos favoritos).

---

## 2. Schemas

### 2.1. `app/schemas/manga_schemas.py` (reescrito)

| Classe | Correção |
|---|---|
| `MangaBase` | + `artista`, `data_lancamento` (date), `capa_url`, `sinopse` |
| `MangaCreate` | herda base completo (cria com artista/data/capa) |
| `MangaUpdate` | **remove** `volumes` e `descricao`; usa `sinopse`; + `artista`, `data_lancamento`, `capa_url` |
| `MangaResponse` | herda base completa + `id`, `criado_em`, `atualizado_em` |
| `VolumeCreate` | `numero` + `comprado` (default `True`) |
| `VolumeUpdate` | **novo** — `numero`, `comprado`, `capa_volume` (todos opcionais) |
| `VolumeResponse` | **novo** — `id`, `manga_id`, `numero`, `comprado`, `capa_volume` |

```python
class MangaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1)
    autor: Optional[str] = Field(None, min_length=1)
    genero: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, min_length=1)
    artista: Optional[str] = None
    data_lancamento: Optional[date] = None
    sinopse: Optional[str] = None          # antes "descricao" (inexistente no model)
    capa_url: Optional[str] = None
```

### 2.2. `app/schemas/livro_schemas.py` (reescrito)

- `descricao` → **`sinopse`** (campo real do model).
- + `isbn`, `data_publicacao`, `capa_url`.
- `LivroController.criar` passou a usar `Livro(**dados.model_dump())` (sem mapeamento manual).

### 2.3. `svhemas_favoritos.py` → `app/schemas/favoritos_schemas.py`

- Renomeado (typo corrigido).
- Schemas reescritos para casar com o que a API retorna: `id`, `usuario_id`, `livro_id`/`manga_id`, `titulo`.
- `orm_mode = True` (pydantic v1) → `model_config = ConfigDict(from_attributes=True)`.

---

## 3. Controllers

### 3.1. `favoritos_controller.py`
As associações (`UsuarioFavoritoLivro/Manga`) não têm coluna `titulo`. O controller agora
**serializa** incluindo o título do relacionamento:

```python
def _serializar_manga(favorito):
    return {
        "id": favorito.id,
        "usuario_id": favorito.usuario_id,
        "manga_id": favorito.manga_id,
        "titulo": favorito.manga.titulo,   # lazy load no relacionamento
    }
```

- `adicionar_favorito`/`listar_favoritos` retornam dicts prontos para o `response_model`.
- `remover_favorito` retorna `{"msg": ...}` (antes `{"detail": ...}`).

### 3.2. `manga_volume_controller.py`
- `adicionar_volume(db, manga_id, dados: VolumeCreate)` — usa `dados.numero`, `dados.comprado`.
- `atualizar_volume(db, manga_id, numero, dados: VolumeUpdate)` — aplica campos opcionais;
  ao renumerar, checa conflito de número.

### 3.3. `usuario_controller.py` — **removido**
- Dead code quebrado: `criar_usuario` gravava em `senha_hash` (coluna é `senha`) e o
  registro real é feito em `rota_registro.py`.
- O único uso era `buscar_por_email` no `autenticar_controller.py` → substituído por
  `db.query(Usuario).filter(Usuario.email == email).first()`.

### 3.4. Deleção simplificada (CASCADE do banco)
- `MangaController.deletar` e `LivroController.deletar` agora só fazem `db.delete(...)` —
  os favoritos (e volumes) são removidos pelas FKs `ON DELETE CASCADE` da Sprint 3.
- `LivroController.upload_capa` corrigido: gravava em `capa_livro` (coluna removida na
  Sprint 3 → crash garantido) → agora grava em `capa_url`. A reescrita completa
  (Cloudinary, sem bytes em coluna String) é a **Sprint 5**.

---

## 4. Rotas — response models e limpeza

### 4.1. `rotas_mangas.py`
- **Removida** a rota `/teste-admin` (só existia para smoke test da Sprint 2).
- Todos os endpoints com `response_model`:
  - `list[ MangaResponse ]` (GET / e listar volumes);
  - `MangaResponse` (GET/{id}, POST, PUT);
  - `VolumeResponse` (POST/PUT volumes, GET volume);
- `PUT /{manga_id}/volumes/{numero}` agora recebe **`VolumeUpdate` no body**
  (antes: query param `comprado`).
- `POST /{manga_id}/volumes` recebe `VolumeCreate` (body) e passa ao controller.

### 4.2. `rotas_livros.py`
- `list[ LivroResponse ]` / `LivroResponse` em listar/obter/criar/atualizar.

### 4.3. `rotas_favoritos_mangas.py` e `rotas_favoritos_livros.py`
- Typo **`routa_favoritos_livros` → `rota_favoritos_livros`** (variável/import em `main.py`).
- Response models `FavoritoMangaResponse`/`FavoritoLivroResponse`.

### 4.4. `app/main.py`
- Import/registro do router de favoritos de livros corrigido.

---

## 5. Arquivos removidos

```
app/schemas/svhemas_favoritos.py   (→ favoritos_schemas.py)
app/controllers/usuario_controller.py   dead code quebrado
app/teste.py                        script manual (cria token no import)
app/requirements.txt                duplicata obsoleta (Dockerfile usa requirements.txt da raiz)
```

> `app/teste.py` executava código **no import** (criava token JWT só por importar).
> Removido — perigo de side-effect.

---

## 6. Validações realizadas

| Etapa | Resultado |
|---|---|
| `MangaCreate` completo (artista, data_lancamento, capa_url) | ✅ 201 |
| `PUT /mangas/{id}` com `sinopse` e `status` | ✅ 200 (campos aplicados) |
| `POST volumes` com `comprado` no body | ✅ 201 |
| `PUT /volumes/{numero}` com `VolumeUpdate` body | ✅ 200 (`comprado`+`capa_volume`) |
| Favoritar mangá → `titulo` no response | ✅ 200 `{"titulo": "Naruto"}` |
| Listar favoritos | ✅ 200 lista com títulos |
| Remover favorito | ✅ 200 |
| Criar livro com `isbn`+`sinopse` | ✅ 201 |
| `/teste-admin` fora do `app.routes` | ✅ |
| `alembic check` | ✅ 0 drift |
| `pytest` | ✅ baseline (2 passed, 5 errors — conftest, Sprint 6) |
| Docker (rebuild + GET /mangas/) | ✅ OK |

---

## 7. Achados para sprints futuras

1. **Sprint 5 (Cloudinary):** os 3 `upload_capa` ainda leem **bytes binários** e gravam em
   coluna `String` — bug conhecido (funciona só para texto/ASCII). Será substituído por
   upload real (validação de tamanho/tipo, URL gravada).
2. **Sprint 6 (testes):** `test_volumes` provavelmente chama PUT com `comprado` como query
   param — será reescrito junto com o conftest.
3. Rotas de favoritos seguem com prefixos singulares/plurais mistos
   (`/favoritos/manga` vs `/favoritos/livros`) — mantido para não quebrar o frontend.

---

## 8. Próximos passos (Sprint 5 — Upload de capas via Cloudinary)

- `CLOUDINARY_URL` na config + SDK; endpoints `upload-capa` salvam no Cloudinary e gravam
  a **URL** em `capa_url`/`capa_volume`.
- Validação: tamanho máx. 5MB, content-type e extensões permitidas.
- Corrigir a leitura binária em colunas `String` (bug atual).
- Atualizar `docs/ROTEIRO_DEPLOY.md` com o passo a passo Cloudinary.