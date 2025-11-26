from fastapi import FastAPI
from app.database.conexao import Base, criacao as engine
from app.routers.rotas_autentica import rota as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

