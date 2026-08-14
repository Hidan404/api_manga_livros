"""Registro central de models.

Importar este pacote garante que TODOS os models sejam registrados na
`Base.metadata` e no registry de relacionamentos (names em string).
Essencial para scripts standalone (seed_admin, testes) e para o Alembic.
"""

from app.models.favoritos_model import UsuarioFavoritoLivro, UsuarioFavoritoManga
from app.models.livros_model import Livro
from app.models.manga_model import Manga
from app.models.manga_volume_model import MangaVolume
from app.models.refresh_token_model import RefreshToken
from app.models.usuario_model import Usuario

__all__ = [
    "Usuario",
    "Manga",
    "MangaVolume",
    "Livro",
    "UsuarioFavoritoLivro",
    "UsuarioFavoritoManga",
    "RefreshToken",
]
