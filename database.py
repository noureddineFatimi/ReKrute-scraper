from sqlmodel import SQLModel, create_engine, Session
from config import DATABASE_URL

from models.database import SearchJob, Offer

DATABASE_URL = DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)