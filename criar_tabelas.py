from app.database.conexao import Base, criacao

from app.models.favoritos_model import UsuarioFavoritoLivro, UsuarioFavoritoManga
from app.models.livros_model import Livro
from app.models.manga_model import Manga
from app.models.manga_volume_model import MangaVolume
from app.models.usuario_model import Usuario


Base.metadata.create_all(bind=criacao)
print("Tabelas criadas ")