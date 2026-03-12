# 📚 API Manga Livros

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-framework-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-blue)
![Pytest](https://img.shields.io/badge/tests-pytest-orange)
![License](https://img.shields.io/badge/license-MIT-green)

API REST para gerenciamento de **coleção pessoal de mangás e livros**.

O sistema permite:

* cadastro de usuários
* autenticação segura com JWT
* gerenciamento de mangás
* controle de volumes
* gerenciamento de livros
* sistema de favoritos
* upload de capas
* testes automatizados

Projeto desenvolvido para estudo de **arquitetura backend e APIs modernas em Python**.

---

# 🧠 Arquitetura do Projeto

A API segue uma arquitetura organizada em camadas:

```
Cliente
   │
   ▼
FastAPI (Routers)
   │
   ▼
Controllers
   │
   ▼
Services / Utils
   │
   ▼
Models (SQLAlchemy)
   │
   ▼
PostgreSQL
```

Estrutura real do projeto:

```
app/
 ├── controllers
 ├── core
 ├── database
 ├── models
 ├── routers
 ├── schemas
 ├── utils
 ├── main.py
```

Essa arquitetura facilita:

* manutenção
* testes
* escalabilidade
* separação de responsabilidades

---

# 🔐 Fluxo de Autenticação

```
Usuário
   │
   ▼
POST /auth/register
   │
   ▼
POST /auth/login
   │
   ▼
Recebe JWT Token
   │
   ▼
Authorization: Bearer TOKEN
   │
   ▼
Acesso às rotas protegidas
```

---

# 🚀 Tecnologias Utilizadas

Backend:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* Passlib
* JWT

Testes:

* Pytest

Servidor:

* Uvicorn

---

# ⚙️ Instalação

Clone o projeto:

```
git clone https://github.com/Hidan404/api_manga_livros.git
```

Entre na pasta:

```
cd api_manga_livros
```

Crie ambiente virtual:

```
python -m venv .venv
```

Ative o ambiente:

Linux / macOS

```
source .venv/bin/activate
```

Instale dependências:

```
pip install -r requirements.txt
```

---

# 🗄️ Banco de Dados

Configure o PostgreSQL:

```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/manga_livros
```

Tabelas do banco:

```
usuarios
mangas
livros
manga_volumes
usuarios_favoritos_mangas
usuarios_favoritos_livros
```

---

# ▶️ Executando a API

Inicie o servidor:

```
uvicorn app.main:app --reload
```

A API estará disponível em:

```
http://127.0.0.1:8000
```

Documentação interativa:

```
http://127.0.0.1:8000/docs
```

---

# 📡 Endpoints Principais

## Autenticação

POST `/auth/register` → Registrar usuário

POST `/auth/login` → Login

POST `/auth/refresh` → Refresh token

---

# 📚 Livros

GET `/livros/`

POST `/livros/`

GET `/livros/{livro_id}`

PUT `/livros/{livro_id}`

DELETE `/livros/{livro_id}`

---

# 📖 Mangás

GET `/mangas/`

POST `/mangas/`

GET `/mangas/{manga_id}`

PUT `/mangas/{manga_id}`

DELETE `/mangas/{manga_id}`

POST `/mangas/teste-admin`

---

# 📦 Volumes de Mangá

GET `/mangas/{manga_id}/volumes`

POST `/mangas/{manga_id}/volumes`

GET `/mangas/{manga_id}/volumes/{numero}`

PUT `/mangas/{manga_id}/volumes/{numero}`

DELETE `/mangas/{manga_id}/volumes/{numero}`

---

# 🖼️ Upload de Capas

POST `/mangas/{manga_id}/upload-capa`

POST `/mangas/{manga_id}/volumes/{numero}/upload-capa`

---

# ⭐ Favoritos

### Mangás

POST `/favoritos/manga/{manga_id}`

GET `/favoritos/manga/`

DELETE `/favoritos/manga/{favorito_id}`

### Livros

POST `/favoritos/livros/{livro_id}`

GET `/favoritos/livros/`

DELETE `/favoritos/livros/{favorito_id}`

---

# 🧪 Testes

O projeto possui testes automatizados com Pytest.

Executar testes:

```
pytest -v
```

---

# 📸 Demonstração

Adicionar imagens aqui:

```
docs/swagger.png
docs/api.png
```

Exemplo:

```
![API Docs](docs/swagger.png)
```

---

# 📈 Melhorias Futuras

* Docker
* CI/CD
* Paginação
* busca por mangás
* dashboard web

---

# 👨‍💻 Autor

Ronald Sousa

Desenvolvedor backend em formação.

GitHub:

https://github.com/Hidan404
