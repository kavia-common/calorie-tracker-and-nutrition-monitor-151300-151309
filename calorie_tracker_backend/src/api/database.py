import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env, must be present at project root
load_dotenv()

# PUBLIC_INTERFACE
def get_database_url():
    """
    Returns the SQLALCHEMY_DATABASE_URL from environment variables.
    Database configuration is specified in the environment for deployment flexibility.
    """
    return os.getenv("CALORIE_TRACKER_DATABASE_URL", "sqlite:///./calories.db")

SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
