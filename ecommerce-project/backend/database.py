"""
database.py
-----------
Sets up the database connection using SQLAlchemy.

It reads the connection string from the DATABASE_URL environment variable.
- If you do nothing, it uses a local SQLite file (ecommerce.db) so the
  project runs instantly on any machine with no extra setup.
- For your Supabase PostgreSQL database, just set DATABASE_URL in the .env
  file (see .env.example) and everything else stays the same.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from the .env file into the environment.
load_dotenv()

# Read the database URL. If it is not set, fall back to a local SQLite file.
# Example Supabase value:
# postgresql://postgres:YOURPASSWORD@db.xxxx.supabase.co:5432/postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

# SQLite needs a special argument to work with FastAPI's threading.
# PostgreSQL does not need it, so we only add it for SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# The engine is the core interface to the database.
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# SessionLocal is a factory that creates new database sessions (one per request).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our ORM models (tables) will inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency.
    Opens a database session for a single request and always closes it
    afterwards, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
