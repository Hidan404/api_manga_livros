from passlib.context import CryptContext

pwd_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SenhaHasher:

    @staticmethod
    def hash_criar(senha: str) -> str:
        senha = senha.encode("utf-8")[:72].decode("utf-8")
        return pwd_contexto.hash(senha)

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str) -> bool:
        return pwd_contexto.verify(senha, senha_hash)
 