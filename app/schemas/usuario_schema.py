from pydantic import BaseModel, EmailStr

class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str | None = "user"

class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: str

    class Config:
        para_atributos = True
