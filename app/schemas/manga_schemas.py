from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

#@ Schemas para o modelo Manga
# Base para evitar repetição
class MangaBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    volumes: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(
        None,
        description="Ex: 'Em andamento', 'Concluído', 'Hiato'"
    )
    descricao: Optional[str] = None


class MangaCreate(MangaBase):
    # Todo: adicionar validações específicas se necessário
    pass


class MangaUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    volumes: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None
    descricao: Optional[str] = None


class MangaResponse(MangaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
