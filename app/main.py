from fastapi import FastAPI
from app.database.conexao import Base, criacao as engine
from app.routers.rotas_autentica import rota as auth_router
from app.routers.rotas_livros import rota_livros
from app.routers.rotas_mangas import rota_mangas
from app.routers.rotas_favoritos_mangas import rota_favoritos_manga
from app.routers.rotas_favoritos_livros import routa_favoritos_livros
from app.routers.rota_registro import rota as rota_registro
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Manga Livros",
    description="""
API para gerenciamento de coleções de mangás e livros.

Funcionalidades principais:

- Autenticação com JWT
- Gerenciamento de Mangás
- Controle de Volumes
- Gerenciamento de Livros
- Sistema de Favoritos
- Upload de capas
""",
    version="1.0.0",
    contact={
        "name": "Ronald Sousa",
        "url": "https://github.com/Hidan404",
    }
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost",
    "http://127.0.0.1",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(rota_livros)
app.include_router(rota_mangas)
app.include_router(rota_favoritos_manga)
app.include_router(routa_favoritos_livros)
app.include_router(rota_registro)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)



