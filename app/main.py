from fastapi import FastAPI
from app.database.conexao import Base, criacao as engine
from app.routers.rotas_autentica import rota as auth_router
from app.routers.rotas_livros import rota_livros
from app.routers.rotas_mangas import rota_mangas
from app.routers.rotas_favoritos_mangas import rota_favoritos_manga
from app.routers.rotas_favoritos_livros import routa_favoritos_livros
from app.routers.rota_registro import rota as rota_registro

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(rota_livros)
app.include_router(rota_mangas)
app.include_router(rota_favoritos_manga)
app.include_router(routa_favoritos_livros)
app.include_router(rota_registro)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

