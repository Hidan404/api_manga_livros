from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Importa a configuração da aplicação para obter a URL do banco
from app.core.configuracao import config as app_config

# Importa a Base e TODOS os models para popular o metadata do autogenerate
from app.database.conexao import Base
from app.models import (  # noqa: F401
    favoritos_model,
    livros_model,
    manga_model,
    manga_volume_model,
    refresh_token_model,
    usuario_model,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# A URL do banco vem da configuração da aplicação (ambiente / .env),
# NÃO do alembic.ini — evita duplicar a connection string em dois lugares.
#
# IMPORTANTE: NÃO usar `config.set_main_option("sqlalchemy.url", ...)` aqui.
# O configparser do Alembic faz interpolação de `%` e quebra com senhas
# URL-encodadas (ex.: `%40` em `@`). Por isso a URL é passada direto ao
# create_engine abaixo, sem transitar pelo configparser.

# Metadata de todos os models registrados (Base declarativa)
target_metadata = Base.metadata


def _connect_args() -> dict:
    """sslmode específico do PostgreSQL (Supabase exige `require`)."""
    connect_args: dict = {}
    if app_config.DATABASE_URL.startswith("postgresql"):
        connect_args["sslmode"] = app_config.SSL_MODE
    return connect_args


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configura o context apenas com a URL, sem criar Engine.
    Útil para gerar SQL sem conectar (ex.: `alembic upgrade head --sql`).
    """
    context.configure(
        url=app_config.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (conecta no banco de verdade)."""
    connectable = create_engine(
        app_config.DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args=_connect_args(),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
