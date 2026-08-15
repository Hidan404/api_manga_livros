"""Cria (ou promove) o usuário administrador (Sprint 2).

Como usar:
    python seed_admin.py

As variáveis ADMIN_EMAIL e ADMIN_SENHA são lidas do ambiente ou do `.env`.

`ADMIN_SENHA` pode ser:
  - uma senha em texto puro (o script gera o hash bcrypt); ou
  - um hash bcrypt já pronto (formato `$2b$...`) — recomendado para não
    manter a senha em texto puro em lugar nenhum.
"""

import os

from dotenv import load_dotenv

from app.core.roles import RoleUsuario
from app.database.conexao import SessionLocal
from app.models import Usuario
from app.utils.senha_hasher import SenhaHasher

load_dotenv()  # carrega ADMIN_EMAIL/ADMIN_SENHA do .env


def _hash_da_senha(senha: str) -> str:
    """Usa a senha direto se já for bcrypt; caso contrário gera o hash."""
    if senha.startswith("$2"):
        return senha
    return SenhaHasher.hash_criar(senha)


def criar_admin() -> None:
    email = os.getenv("ADMIN_EMAIL")
    senha = os.getenv("ADMIN_SENHA")
    nome = os.getenv("ADMIN_NOME", "Administrador")

    if not email or not senha:
        print("❌ Defina ADMIN_EMAIL e ADMIN_SENHA (variáveis de ambiente).")
        return

    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario:
            usuario.role = RoleUsuario.ADMIN.value
            print(f"✅ Usuário {email} promovido para admin.")
        else:
            db.add(Usuario(
                nome=nome,
                email=email,
                senha=_hash_da_senha(senha),
                role=RoleUsuario.ADMIN.value,
            ))
            print(f"✅ Admin criado: {email}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    criar_admin()
