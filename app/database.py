import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Delcaration de var depuis env
load_dotenv()
db_url=os.getenv("db_url_env")

# DB setup
engine=create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
MyBase=declarative_base()

# --- Fonction db
def get_db():
    db=SessionLocal()
    try:
        yield db 
    finally:
        db.close()
 
