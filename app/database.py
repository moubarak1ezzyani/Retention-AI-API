import os
from dotenv import load_dotenv
from slqalchemy import create_engine, Integer, String, Column, Datetime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from slqalchemy.sql import func

# Delcaration de var depuis env
load_dotenv()
db_url=os.getenv("db_url_env")

# DB setup
engine=create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
MyBase=declarative_base()

# Table sql orm :  id timestamp userid employeeid probability
class UserDB(MyBase):
    __tablename__="users"
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, index=True)
    password_hash=Column(String) 
    created_at=Column(Datetime(timezone=True), server_default=func.now())
    update_at=Column(Datetime(timezone=True, onupdate=func.now()))

class prediction_history(MyBase):
    __tablename__="prediction_history"
    id=Column(Integer, primary_key=True, index=True)
    timestamp=Column(Datetime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('UserDB.id')) 
    employee_id = Column(Integer) 
    probability=Column(Float)

# --- Fonction db
def get_db():
    db=SessionLocal()
    try:
        yield db 
    finally:
        db.close()
 
