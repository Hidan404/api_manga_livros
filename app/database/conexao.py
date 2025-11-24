from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

criacao = create_engine(SQLALCHEMY_DATABASE_URL)

sessao_local = sessionmaker(autocommit=False, autoflush=False, bind=criacao)

Base = declarative_base()

def get_db():
    db = sessao_local()
    try:
        yield db
    finally:
        db.close()
