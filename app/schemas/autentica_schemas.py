from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(BaseModel):
    refresh_token: str
