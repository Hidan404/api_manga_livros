from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# Schemas para o modelo Livro
# Base para evitar repetição
class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    genero: str | None = None
    isbn: str | None = Field(None, max_length=20)
    data_publicacao: date | None = None
    ano: int | None = Field(None, ge=0)
    sinopse: str | None = None
    capa_url: str | None = None


class LivroCreate(LivroBase):
    pass


class LivroUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=1)
    autor: str | None = Field(None, min_length=1)
    genero: str | None = None
    isbn: str | None = Field(None, max_length=20)
    data_publicacao: date | None = None
    ano: int | None = Field(None, ge=0)
    sinopse: str | None = None
    capa_url: str | None = None


class LivroResponse(LivroBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
