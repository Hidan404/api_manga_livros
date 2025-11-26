from passlib.context import CryptContext

pwd_contexto = CryptContext(schemes=["bcrypt"])

class SenhaHasher():
    
    @staticmethod
    def hash_criar(senha: str) -> str:
        senha2 = senha[:72]
        print(type(pwd_contexto.hash(senha2)))
        return pwd_contexto.hash(senha2)
    
    @staticmethod
    def verificar_senha(senha: str, senha_hash: str) -> bool:
        return pwd_contexto.verify(senha, senha_hash)
    

#s = SenhaHash()
#s.hash_criar("hidanexagonal")    