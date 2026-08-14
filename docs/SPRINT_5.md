# ☁️ Sprint 5 — Upload de capas (Cloudinary)

> Documento detalhado do que foi feito na Sprint 5.
> Data: 2026-08-14 · Situação: **concluída**
> Plano de referência: [`PLANO_DE_MELHORIAS.md`](../PLANO_DE_MELHORIAS.md) (decisão #1)
> Sprint anterior: [`SPRINT_4.md`](SPRINT_4.md)

---

## 1. Objetivo da Sprint 5

Imagens **fora do Postgres** — a API envia o arquivo ao Cloudinary e grava apenas a
**URL** em `capa_url`/`capa_volume`:

- configurar o SDK a partir de `CLOUDINARY_URL`;
- validar arquivo antes do upload (tamanho, content-type, extensão);
- corrigir o bug de gravar **bytes binários** em coluna `String` (funcionava só para ASCII).

---

## 2. `app/core/capa_upload.py` (novo)

### 2.1. Configuração do SDK

`CLOUDINARY_URL` tem o formato `cloudinary://<api_key>:<api_secret>@<cloud_name>`.
A config (pydantic-settings) lê do `.env`, mas **não** exporta para `os.environ` — por isso
o SDK é configurado explicitamente:

```python
from urllib.parse import urlparse

parsed = urlparse(config.CLOUDINARY_URL)
cloudinary.config(
    cloud_name=parsed.hostname,
    api_key=parsed.username,
    api_secret=parsed.password,
    secure=True,          # URLs https://
)
```

- URL ausente/malformada → `_configurar_sdk()` retorna `False` → endpoint responde **503**.

### 2.2. Validação do arquivo

```python
TAMANHO_MAXIMO = 5 * 1024 * 1024        # 5 MB
CONTENT_TYPES_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}
EXTENSOES_PERMITIDAS = {"jpg", "jpeg", "png", "webp", "gif"}
```

| Checagem | Falha → |
|---|---|
| `content-type` não permitido | `400` |
| extensão não permitida (double-check do tipo) | `400` |
| arquivo vazio | `400` |
| > 5 MB | `400` |

A validação roda **antes** do check de credencial → arquivo inválido sempre devolve
`400` mesmo com Cloudinary desconfigurado.

### 2.3. Upload

```python
resultado = cloudinary.uploader.upload(
    io.BytesIO(conteudo),        # bytes → file-like
    folder=pasta,                # ex.: "mangas/3/volumes"
    public_id=public_id,         # ex.: "1"
    overwrite=True,
    resource_type="image",
)
return resultado["secure_url"]
```

- Erro do SDK → **502** ("Falha ao enviar imagem ao Cloudinary").
- Falta `secure_url` na resposta → **502**.

---

## 3. Controllers atualizados (URL em vez de bytes)

| Controller | Método | Pasta Cloudinary | public_id |
|---|---|---|---|
| `MangaController` | `upload_capa` | `mangas` | `manga.id` |
| `MangaVolumeController` | `upload_capa_volume` | `mangas/{manga_id}/volumes` | `numero` |
| `LivroController` | `upload_capa` | `livros` | `livro.id` |

Todos passaram de:

```python
manga.capa_url = arquivo.file.read()   # ❌ bytes binários em coluna String
```

para:

```python
url = fazer_upload(arquivo, pasta="mangas", public_id=str(manga.id))
manga.capa_url = url                   # ✅ URL pública
```

---

## 4. Rotas

`POST /livros/{livro_id}/upload-capa` foi **adicionada** em `rotas_livros.py` (o controller
já existia desde a Sprint 4; a rota faltava). Rotas de upload (todas admin):

```
POST /mangas/{manga_id}/upload-capa
POST /mangas/{manga_id}/volumes/{numero}/upload-capa
POST /livros/{livro_id}/upload-capa
```

---

## 5. Dependência

`cloudinary==1.45.0` adicionado a `requirements.txt`.

---

## 6. Validações realizadas

| Etapa | Resultado |
|---|---|
| Arquivo `text/plain` → upload | ✅ `400` "Tipo de arquivo não permitido" |
| Arquivo `capa.exe` com content-type `image/png` | ✅ `400` "Extensão não permitida" |
| PNG válido sem `CLOUDINARY_URL` | ✅ `503` "Upload não configurado" |
| Parsing de `cloudinary://abc:def@mycloud` no SDK | ✅ `cloud_name=mycloud, api_key=abc, api_secret=def` |
| URL ausente → `_configurar_sdk()` | ✅ `False` |
| 3 rotas de upload registradas no `app.routes` | ✅ |
| `pytest` | ✅ baseline (2 passed, 5 errors — conftest, Sprint 6) |
| Docker (rebuild) | ✅ |

> ⚠️ O fluxo feliz (upload real com credencial) **não foi testado** — o usuário perdeu as
> secrets do Cloudinary. O código está pronto; basta definir `CLOUDINARY_URL` real e testar
> via `POST /mangas/{id}/upload-capa`.

---

## 7. Documentação

`docs/ROTEIRO_DEPLOY.md` ganhou a seção **5.5 — Cloudinary**: como criar a conta, onde
colar a URL (env do Render), como a API usa (validações e endpoints) e tabela de erros.

---

## 8. Arquivos tocados

```
app/core/capa_upload.py              NOVO
app/controllers/manga_controller.py         upload via Cloudinary
app/controllers/manga_volume_controller.py  upload via Cloudinary
app/controllers/livro_controller.py         upload via Cloudinary
app/routers/rotas_livros.py                 + rota upload-capa de livro
requirements.txt                            + cloudinary==1.45.0
docs/ROTEIRO_DEPLOY.md                      seção 5.5 (Cloudinary)
PLANO_DE_MELHORIAS.md                       Sprint 5 marcada
```

---

## 9. Próximos passos (Sprint 6 — Testes, CI e qualidade)

- Refatorar conftest: banco isolado (fixture), remover dependência de `hidan@gmail.com`;
  fixture cria usuário admin.
- Cobrir: auth (cookies, refresh, revogação), CRUD, favoritos, upload.
- CI GitHub Actions rodando `pytest`; lint `ruff`; endpoint `/health` + logging.
- Testar upload real com a `CLOUDINARY_URL` de verdade quando disponível.