from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- Database URL Configuration ---
# It's best practice to get this from an environment variable.
# Example: DATABASE_URL = "postgresql://user:password@localhost/triage_db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triage_app.db")

# --- SQLAlchemy Engine ---
# The engine is the central point of communication with the database.
# 'connect_args' is only needed for SQLite to allow multithreaded access.
engine_args = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_args)

# --- Database Session ---
# A SessionLocal class is a factory for new database sessions.
# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Declarative Base ---
# We will inherit from this class to create each of the ORM models (database tables).
Base = declarative_base()

# --- Dependency for FastAPI ---
# A helper function to get a database session for each request and ensure it's closed afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
