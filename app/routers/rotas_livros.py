from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.controllers.livro_controller import LivroController
from app.core.dependecia_auth import get_current_user, require_role
from app.database.conexao import get_db
from app.schemas.livro_schemas import LivroCreate, LivroResponse, LivroUpdate

rota_livros = APIRouter(prefix="/livros", tags=["Livros"])


@rota_livros.get("/", summary="Listar livros", description="Retorna uma lista de todos os livros disponíveis.", response_model=list[LivroResponse])
def listar_livros(db: Session = Depends(get_db)):
    return LivroController.listar(db)


@rota_livros.get("/{livro_id}", summary="Obter livro", description="Retorna os detalhes de um livro específico.", response_model=LivroResponse)
def obter_livro(livro_id: int, db: Session = Depends(get_db)):
    return LivroController.obter_por_id(db, livro_id)


# Somente ADMIN pode criar livro
@rota_livros.post("/", summary="Criar livro", description="Cria um novo livro com os dados fornecidos.", dependencies=[Depends(require_role("admin"))], status_code=201, response_model=LivroResponse)
def criar_livro(
    dados: LivroCreate,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return LivroController.criar(db, dados)


# Somente ADMIN pode atualizar livro
@rota_livros.put("/{livro_id}", summary="Atualizar livro", description="Atualiza os dados de um livro específico.", dependencies=[Depends(require_role("admin"))], response_model=LivroResponse)
def atualizar_livro(
    livro_id: int,
    dados: LivroUpdate,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return LivroController.atualizar(db, livro_id, dados)


# Somente ADMIN pode deletar
@rota_livros.delete("/{livro_id}", dependencies=[Depends(require_role("admin"))], summary="Deletar livro", description="Remove um livro específico do sistema.")
def deletar_livro(
    livro_id: int,
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return LivroController.deletar(db, livro_id)


@rota_livros.post("/{livro_id}/upload-capa", summary="Upload de capa de livro", description="Faz upload da capa de um livro específico.", dependencies=[Depends(require_role("admin"))])
def upload_capa_livro(
    livro_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_logado=Depends(get_current_user)
):
    return LivroController.upload_capa(db, livro_id, arquivo)
