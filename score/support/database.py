from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from os import getenv
load_dotenv()


db_uri = getenv('DATABASE_URL')
if 'postgresql' not in db_uri:
    db_uri = db_uri.replace('postgres', 'postgresql')

engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# create database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
