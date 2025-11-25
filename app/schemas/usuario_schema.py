from pydantic import BaseModel, EmailStr

class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    senha: str
