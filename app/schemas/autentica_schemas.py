from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"