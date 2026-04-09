import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# Get the PostgreSQL URL from the .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env file!")

# Create the PostgreSQL Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for your database models
Base = declarative_base()