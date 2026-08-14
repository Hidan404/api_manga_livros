from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# Schemas para o modelo Manga
# Base para evitar repetição
class MangaBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    genero: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    artista: str | None = None
    data_lancamento: date | None = None
    sinopse: str | None = None
    capa_url: str | None = None


class MangaCreate(MangaBase):
    pass


class MangaUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=1)
    autor: str | None = Field(None, min_length=1)
    genero: str | None = Field(None, min_length=1)
    status: str | None = Field(None, min_length=1)
    artista: str | None = None
    data_lancamento: date | None = None
    sinopse: str | None = None
    capa_url: str | None = None


class MangaResponse(MangaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class VolumeCreate(BaseModel):
    numero: int = Field(..., ge=1)
    comprado: bool = True


class VolumeUpdate(BaseModel):
    numero: int | None = Field(None, ge=1)
    comprado: bool | None = None
    capa_volume: str | None = None


class VolumeResponse(BaseModel):
    id: int
    manga_id: int
    numero: int
    comprado: bool
    capa_volume: str | None = None

    model_config = ConfigDict(from_attributes=True)
