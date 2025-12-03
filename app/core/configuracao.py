from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class Configuracao(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "Ronald123")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",60))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "chave_refresh_secreta")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 dias


config = Configuracao()