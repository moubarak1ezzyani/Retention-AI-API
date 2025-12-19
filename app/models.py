from slqalchemy import Integer, String, Column, Datetime, ForeignKey, Float
from slqalchemy.sql import func
from .database import MyBase

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