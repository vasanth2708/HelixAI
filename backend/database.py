# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Create the SQLAlchemy engine
engine = create_engine(Config.DATABASE_URL, echo=False, future=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Create a Base class for declarative models
Base = declarative_base()