from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.core.logging_config import configurar_logging
from app.core.rate_limit import limiter
from app.database.conexao import engine
from app.routers.rota_registro import rota as rota_registro
from app.routers.rotas_autentica import rota as auth_router
from app.routers.rotas_favoritos_livros import rota_favoritos_livros
from app.routers.rotas_favoritos_mangas import rota_favoritos_manga
from app.routers.rotas_livros import rota_livros
from app.routers.rotas_mangas import rota_mangas

configurar_logging()

app = FastAPI(
    title="API Manga Livros",
    description="""
API para gerenciamento de coleções de mangás e livros.

Funcionalidades principais:

- Autenticação com JWT (access + refresh via cookies HttpOnly)
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

# Rate limiting (Sprint 2) — contadores em memória por processo
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health", tags=["Saúde"], summary="Health check",
         description="Verifica se a API responde e se o banco está acessível.")
def health():
    banco = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        banco = "indisponível"
    return {"status": "ok", "versao": app.version, "banco": banco}

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://0.0.0.0",
    "http://127.0.0.1",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://seudominio.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(rota_livros)
app.include_router(rota_mangas)
app.include_router(rota_favoritos_manga)
app.include_router(rota_favoritos_livros)
app.include_router(rota_registro)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8109, reload=True)



