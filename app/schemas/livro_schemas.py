from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Schemas para o modelo Livro
# Base para evitar repetição
class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    descricao: Optional[str] = None
    ano: Optional[int] = Field(None, ge=0)
    genero: Optional[str] = None


# Para criacao
class LivroCreate(LivroBase):
    pass
    


# Para atualização parcial (campos opcionais)
class LivroUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    descricao: Optional[str] = None
    ano: Optional[int] = Field(None, ge=0)
    genero: Optional[str] = None


# O que retorna da API
class LivroResponse(LivroBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True   # compatível com SQLAlchemy
