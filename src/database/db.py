from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import psycopg2
import os
from dotenv import load_dotenv
from src.conf.config import settings

load_dotenv()

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
