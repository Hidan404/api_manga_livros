from pydantic import BaseModel


class FavoritoLivroBase(BaseModel):
    livro_id: int


class FavoritoLivroResponse(BaseModel):
    favorito_id: int
    livro_id: int
    titulo: str

    class Config:
        orm_mode = True


class FavoritoMangaBase(BaseModel):
    manga_id: int


class FavoritoMangaResponse(BaseModel):
    favorito_id: int
    manga_id: int
    titulo: str

    class Config:
        orm_mode = True

