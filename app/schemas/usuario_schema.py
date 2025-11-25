from pydantic import BaseModel, EmailStr

class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        para_atributos = True
