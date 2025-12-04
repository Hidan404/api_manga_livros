from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexao import get_db
from app.schemas.autentica_schemas import LoginSchema, TokenResposta
from app.controllers.autenticar_controller import AuthController
from app.schemas.autentica_schemas import RefreshTokenSchema
from app.controllers.autenticar_controller import AuthController

rota = APIRouter(prefix="/auth", tags=["Autenticação"])
auth_controller = AuthController()

#Essa rota realiza o login do usuário
@rota.post("/login", response_model=TokenResposta)
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    return auth_controller.login(db, payload.email, payload.senha)


@rota.post("/refresh")
def refresh_token(payload: RefreshTokenSchema, db: Session = Depends(get_db)):
    return auth_controller.refresh_token(payload.refresh_token, db)


"""
Explicação de cada parte do código:
1. Importações:
   - Importa os módulos necessários do FastAPI, SQLAlchemy e os componentes específicos do aplicativo, como esquemas e controladores.
2. Criação do Roteador:
   - Cria um roteador APIRouter com o prefixo "/auth" e a tag "Autenticação" para agrupar as rotas relacionadas à autenticação.
"""   