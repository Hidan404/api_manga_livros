from pydantic import BaseModel, ConfigDict


class FavoritoLivroResponse(BaseModel):
    id: int
    usuario_id: int
    livro_id: int
    titulo: str

    model_config = ConfigDict(from_attributes=True)


class FavoritoMangaResponse(BaseModel):
    id: int
    usuario_id: int
    manga_id: int
    titulo: str

    model_config = ConfigDict(from_attributes=True)
